from rapidfuzz import fuzz, utils, distance
from tqdm import tqdm
import pandas as pd
import mapply
mapply.init(n_workers=-1, progressbar=False)
from unidecode import unidecode
from nltk import word_tokenize, download
from nltk.corpus import stopwords
download('stopwords')
download('punkt')
download('punkt_tab')

import string
import re
from copy import deepcopy


def _clean_string(s: str) -> str:
    return utils.default_process(
        unidecode(
            re.sub(r'[\W_]+', ' ', str(s))
        )
    )

def _scorer(
    s1: str, 
    s2: str
) -> float:
    c = 0

    try:
        _s1, _s2 = s1.split(), s2.split()

        s1_0, s2_0  = _s1[0], _s2[0] 

        if distance.Hamming.distance(s1_0, s2_0) <= 1:
            c = 1

            s1_1, s2_1 = _s1[1], _s2[1]
            
            if distance.Hamming.distance(s1_1, s2_1) <= 1:
                c = 1.125
            else:
                c = 0.75

        dist = fuzz.token_set_ratio(s1, s2) * c

        return dist
    except:
        return 0

def _distances(
    unique_strings: list[str], 
    column: str,
    stop: set
) -> pd.DataFrame:
    df = pd.DataFrame(
        unique_strings, 
        columns = [column]
    )

    def process(s):
        if type(s) == str:
            return [
                s for s in 
                    word_tokenize(
                        unidecode(
                            _clean_string(s)
                        )
                    ) 
                if 
                    s not in stop 
                    and s not in string.punctuation
                ]
        else:
            return []
    
    def merging(i):
        _r = (
            df_target
                .merge(
                    df_input, 
                    left_on="0_target", 
                    right_on=f"{i}_input", 
                    how="inner", 
                    suffixes=('_target', '_input')
                )
                .drop_duplicates()
                .reset_index(drop=True)
                .drop(
                    ["0_target", f"{i}_input"],
                    axis=1,
                )
        ) 

        return _r 

    df_raw = pd.concat(
        [
            df, 
            pd.DataFrame(
                df[column].mapply(lambda s: process(s)).values.tolist()
            ).fillna("-1")
        ], 
        axis=1
    )

    try:
        df_target = df_raw[[column, 0]]
    except:
        raise pd.errors.EmptyDataError("No data to standardize after preprocessing.")

    df_target.columns = [str(c) + "_target" for c in df_target.columns]

    df_input_cols = [c for c in df_raw.columns if type(c) == int and c <= 5]
    df_input = df_raw[[column, *df_input_cols]]
    df_input.columns = [str(c) + "_input" for c in df_input.columns]

    dfs = pd.concat(
        [
            merging(d) for d 
            in tqdm(df_input_cols, desc="Merging words")
        ]
    ).drop_duplicates(ignore_index=True)

    print("Word similarity:")
    dfs["distances"] = dfs.mapply(
        lambda row: _scorer(
            _clean_string(row[column + "_target"]), 
            _clean_string(row[column + "_input"])
        ), 
        axis=1,
        progressbar=True
    )

    return dfs.set_index(
        [
            column + "_target", 
            column + "_input"
        ]
    )

def _generate_graph(
    graph_dict: dict,
    output_graph_path: str, 
    divide_letters: bool = False
) -> None:
    from pyvis.network import Network
    import networkx as nx

    temp_graph_dict = [ 
        deepcopy(graph_dict) 
    ]
    graph_dict_list = []

    if divide_letters:
        import os

        divide_letters_dict = {
            "a": {}, "b": {}, "c": {}, "d": {}, 
            "e": {}, "f": {}, "g": {}, "h": {},
            "i": {}, "j": {}, "k": {}, "l": {}, 
            "m": {}, "n": {}, "o": {}, "p": {}, 
            "q": {}, "r": {}, "s": {}, "t": {}, 
            "u": {}, "v": {}, "w": {}, "x": {},
            "y": {}, "z": {}
        }
        letters = list(divide_letters_dict.keys())

        for central_node, nodes in temp_graph_dict[0].items():
            try:
                divide_letters_dict[central_node[0].lower()].update({central_node: nodes})
            except:
                pass

        graph_dict_list = list(divide_letters_dict.values())

        graph_dir_suffix = "graphs"
        if not os.path.exists(output_graph_path):
            raise ValueError(f"Directory {output_graph_path} does not exist.")

        try:
            os.mkdir(f"{output_graph_path}/{graph_dir_suffix}")
        except:
            pass

        output_graph_path += f"/{graph_dir_suffix}"
    else:
        graph_dict_list.append(temp_graph_dict[0])

    for i, graph_dict in enumerate(graph_dict_list):
        nx_graph = nx.Graph()
        
        graph = Network(
            notebook=False, 
            cdn_resources='in_line', 
            height="83vh",
            width="100%",
            select_menu=True,
            filter_menu=True,
            neighborhood_highlight=True
        )
        
        graph.from_nx(nx_graph)

        for central_node, nodes in graph_dict.items():
            graph.add_node(
                central_node, 
                label = central_node, 
                title = "CENTROID__" + central_node
            )
            
            for node in nodes:
                name = node[0]
                value = node[1]

                graph.add_node(
                    name, 
                    label = name, 
                    title = "EDGE__" + name
                )

                graph.add_edge(
                    central_node, 
                    name, 
                    value = int(value), 
                    title = f'{int(value)}'
                )

        path = f"{output_graph_path}/output_graph{f'_{letters[i].upper()}' if divide_letters else ''}.html"

        print(f"Saving graph to {path}...")
        graph.save_graph(path)

    return


def standardize(
    words: list[str], 
    threshold: int = 90,
    stop_word_language: str = 'portuguese',
    output_graph_path: str | None = None
) -> dict[str, str]:
    """
    Standardize a list of strings by clustering similar entries and mapping them to a canonical form.

    :param words: The list of input strings to be standardized.
        It is important to provide the list of words as-is to ensure efficiency.
        A crucial aspect of this process is the tokenizer, which requires input strings to contain delimiters such as spaces.
        For example, the word 'João Pessoa - PB' will be tokenized as ['joao', 'pessoa', 'pb'].
    :type words: list[str]

    :param threshold: Similarity threshold for clustering strings. Words with a spelling similarity above this value,
        measured using string similarity with the [rapidfuzz](https://github.com/rapidfuzz/RapidFuzz) library, will be grouped together.
    :type threshold: int, optional

    :param stop_word_language: Language to use for stopword removal during preprocessing.
        See available options in the NLTK data [documentation](https://www.nltk.org/nltk_data/).
    :type stop_word_language: str, optional

    :param output_graph_path: If provided, saves interactive HTML visualizations of the clusters to the given path.
        If the number of unique words in `words` exceeds 2000, a folder named `graphs` will be created to store
        all the graphs, divided by the node's initial letter from A to Z.
        Visualizations are generated using the [pyvis](https://github.com/WestHealth/pyvis) library.
    :type output_graph_path: str or None, optional

    :return: A dictionary mapping each original string to its standardized (canonical) form.
    :rtype: dict[str, str]

    Example usage and expected input/output can be found in the [README.md](https://github.com/guilhermehuther/string_treatment/blob/main/README.md)
    """

    if not words:
        raise ValueError("Data cannot be empty.")

    if not isinstance(words, list) or not all(isinstance(w, str) for w in words):
        raise ValueError(f"Data must be a list[str].")

    print("Starting word standardization...")
    
    graph_dict = dict()

    stop = set(stopwords.words(stop_word_language))

    column = "temp"
    temp_df = pd.DataFrame({
        column: deepcopy(words)
    })

    unique_strings = temp_df[column].unique()

    count_strings = temp_df[column].value_counts()

    transform_dict = {"nan": "nan"}

    print("Preprocessing unique words...")
    df_distances = _distances(
        unique_strings, 
        column, 
        stop
    )

    for us in tqdm(unique_strings, desc="Building clusters"):
        if transform_dict.get(us) is not None: 
            continue
        
        loc_df = df_distances.loc[us]
        
        filter_1 = loc_df[loc_df.distances.values > threshold]
        if len(filter_1) == 0: 
            continue

        filter_2 = filter_1.copy().reset_index()
        filter_2 = df_distances.loc[filter_1.index]
        filter_2 = filter_2[filter_2.distances.values > threshold].reset_index()
        if len(filter_2) == 0:
            continue

        row_centroid = (
            count_strings
                .loc[filter_2[column + "_input"].values]
                .sort_values(ascending=False).index[0]
        )

        filter_input = filter_2[column + "_input"].unique()

        for fi in filter_input:        
            if transform_dict.get(fi) is not None: 
                continue
            
            transform_dict[fi] = row_centroid
        
        graph_dict[row_centroid] = tuple(zip(
            filter_2[column + "_input"].values.tolist(), 
            filter_2["distances"].values.tolist()
        ))

    if output_graph_path:
        print("Generating graph...")
        _generate_graph(
            graph_dict=graph_dict,
            output_graph_path=output_graph_path,
            divide_letters=True if len(graph_dict) >= 2000 else False
        )

    def mapping(s: str) -> str:
        try: 
            return transform_dict[s]
        except: 
            return s

    temp_df[f"_{column}"] = temp_df[column].mapply(lambda s: mapping(s))

    print("Done.")

    return dict(zip(
        temp_df[column], 
        temp_df[f"_{column}"]
    ))
