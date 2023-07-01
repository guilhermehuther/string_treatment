import operator
from jellyfish import jaro_winkler_similarity, damerau_levenshtein_distance, hamming_distance
import numpy as np
import pandas as pd

METRICS_DICT = {
  'jaro_winkler_similarity': jaro_winkler_similarity, 
  'damerau_levenshtein_distance': damerau_levenshtein_distance, 
  'hamming_distance': hamming_distance
}

def treat_unreferenced(strings_compared: list[str], 
                       metric: str = 'jaro_winkler_similarity', 
                       threshold: float = 0.8):
  '''    
  :param: strings_compared: List of strings to be compared.
  :param: metrics: Metric to be used similiraty measurement of distance between strings.
  :param: threshold: Threshold for the metrics similarity values.
  
  :return: List of strings 'corrected'.
  '''

  try:
    metric = METRICS_DICT[metric]
  except:
    raise KeyError("metric must be a string within: 'jaro_winkler_similarity' OR 'damerau_levenshtein_distance' OR 'hamming_distance'.")
  
  if 0 > threshold > 1:
    raise ValueError('Threshold must be between 0 and 1')
  
  already_corrected = list()
  for i in range(len(strings_compared)):
    distances = dict()
    if strings_compared[i] in already_corrected: 
      continue
    for j in range(i, len(strings_compared)):  
      if strings_compared[j] in already_corrected: 
        continue
      
      distances[strings_compared[j]] = metric(strings_compared[i].lower().strip(), strings_compared[j].lower().strip())

    all_distances = pd.DataFrame(data = distances, index = [0]).unstack().reset_index().drop('level_1', axis = 1)

    if metric.__name__ != 'jaro_winkler_similarity':
      all_distances[0] = [(1 - ((all_distances[0].iloc[i] / len(all_distances['level_0'].iloc[i])) ** 2)) for i in range(all_distances.shape[0])]
    
    all_distances = all_distances[all_distances[0] >= threshold]

    if all_distances.empty: 
      continue
    
    all_distances_max_string = all_distances[all_distances[0] == max(all_distances[0])]['level_0'].values[0] 
    
    already_corrected.append(all_distances_max_string)  
      
    strings_compared = np.where(np.isin(strings_compared, all_distances['level_0'].values) == True, all_distances_max_string, strings_compared) 
    
  return strings_compared


def treat_referenced(strings_compared: list[str], 
                     reference: list[str],
                     metric: str = 'jaro_winkler_similarity'):
  '''    
  :param: strings_compared: List of strings to be compared.
  :param: reference: List of reference strings.
  :param: metric: Metric to be used as similiraty measurement of distance between strings.
  
  :return: List of strings 'corrected'.
  '''
  
  try:
    metric = METRICS_DICT[metric]
  except:
    raise KeyError("metric must be a string within: 'jaro_winkler_similarity' OR 'damerau_levenshtein_distance' OR 'hamming_distance'.")
  
  strings_corrected = list()
  comparations = dict()

  for strings in strings_compared:
    for ref in reference:
      comparations[ref] = metric(strings.lower().strip(), ref.lower().strip())

    if metric.__name__ != 'jaro_winkler_similarity':
      strings_corrected.append(
          min(comparations.items(), key = operator.itemgetter(1))[0]
      )
    else:
      strings_corrected.append(
          max(comparations.items(), key = operator.itemgetter(1))[0]
      )

    comparations.clear()

  return strings_corrected