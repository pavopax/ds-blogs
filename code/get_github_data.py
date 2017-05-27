import requests
import time
import numpy as np
import logging


def from_search(query, headers=None):
  """Use github search to return stars + forks for top query result

  requires headers like:
  headers = {'Authorization': 'token %s' % token}
  """
  if headers is None:
    logging.WARNING("Error: need to pass headers to this function.")
  else:
    r = requests.get('https://api.github.com/search/repositories?q=' + query,
                     headers=headers)
    r.raise_for_status()
    try:
      res = r.json()['items'][0]
      return {'package': query, 'repo': res['full_name'],
              'stars': res['stargazers_count'], 'forks': res['forks_count']}
    except:
      return None


def search_from_list_delayed(query_list, headers, size=29, sleeps=61):
  """Split query_list into chunks and get data for each chunk

  Use chunks of size 30 with 60 second delay to accomodate github API query
  limit of 30 per minute.

  """
  chunks = [None] * 1
  if len(query_list) <= size:
    chunks[0] = query_list
  else:
    chunks = np.array_split(np.array(query_list), len(query_list) // size)
  data = []
  for i, chunk in enumerate(chunks):
    logging.info("Running chunk {0} of {1}...".format(i + 1, len(chunks)))
    # use generator to avoid repeat API calls
    data.append([res for res in (from_search(q, headers=headers)
                                 for q in chunk) if res is not None])
    if i + 1 != len(chunks):
      logging.info("Sleeping for {0} s...".format(sleeps))
      time.sleep(sleeps)
  logging.info("DONE.")
  return sum(data, [])          # unlist


if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO)
  with open("secrets/github-token.nogit", "rb") as f:
    token = f.read()
  headers = {'Authorization': 'token %s' % token}
  sample_queries = ['d3', 'Chart.js', 'Raphael', 'Rickshaw', 'morris.js']
  res = search_from_list_delayed(sample_queries, headers, 2, 3)
  print res
