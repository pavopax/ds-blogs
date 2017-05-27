import requests
import logging
import urllib


# NOTE: SO api is NOT case-sensitive
# package_list = ['dplyr', 'digest', 'ggplot2', 'rcpp', 'the']

GLOBAL_PARAMS = {
    "site": "stackoverflow",
    "key": "y38PeNERQJQIC8EPliKAVQ(("  # SO says this key can be public
}


def get_tag_counts(tag_list):
    """"Given tag list, return tag counts as json"""

    formatted_tags = ';'.join(tag_list)
    # use quote() to replace possible spaces in a tag like "scikit learn"
    url = urllib.quote("https://api.stackexchange.com/2.2/tags/" +
                       formatted_tags + "/info",
                       safe="/:;-")

    logging.debug("Requesting url: " + str(url))

    try:
        r = requests.get(url, params=GLOBAL_PARAMS)
        if r.json()['has_more']:
            print "WARNING: Request has more data that is not shown here."
        return r.json()['items']
    except:
        logging.warning("Error in response.")


def get_single_body_count(body_string, tag=None):
  """Given ONE string, return dict with number of SO questions containing it

  Possibly tagged with TAG.
  Uses API param filter=total to only return counts.
  """
  baseurl = 'https://api.stackexchange.com/2.2/search/advanced'
  params = {
    'q': body_string,
    'filter': 'total',
  }
  params.update(GLOBAL_PARAMS)
  if tag:
    params.update({'tagged': tag})
  r = requests.get(baseurl, params=params)
  return {'query': body_string, 'total': r.json()['total'], 'tag': tag}


def get_body_counts(alist, tag=None):
  """Return list of dicts of SO question body counts for each item in alist

  """
  return [get_single_body_count(item, tag=tag) for item in alist]


if __name__ == "__main__":
  import json
  from utils import read_package_txt

  logging.basicConfig(level=logging.INFO)

  # TODO: use new get_body_counts()
  package_list = read_package_txt("data/package-list-from-cran-task-view.txt")
  logging.info("Getting tags...")
  tag_counts = get_tag_counts(package_list)
  logging.info("Getting body counts (<60 seconds)...")
  question_body_counts = {item: get_body_count(item) for item in package_list}
  logging.info("Getting body counts with R tag (<60 seconds)...")
  question_body_counts_r = {item: get_body_count(item, tag='r')
                            for item in package_list}

  logging.info("Writing to disk...")
  with open('data/so_tag_counts.json', 'w') as f:
    json.dump(tag_counts, f)
  with open('data/so_body_counts.json', 'w') as f:
    json.dump(question_body_counts, f)
  with open('data/so_body_counts_r.json', 'w') as f:
    json.dump(question_body_counts_r, f)
  logging.info("DONE.")
