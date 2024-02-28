# code to create dataset of estimates from mp4 paths (links or local paths)
import argparse
import csv
import glob
import json
import multiprocessing
import os
import time

from functools import partial
from methods import dense_OF, sparse_OF, compression_estimator


def estimate_motion(file_path, estimator):
  motion_est = estimator(file_path)
  vidID = file_path.split("/")[-1].split(".")[0]
  return vidID, motion_est

def write_to_csv(results, output_path):
  with open(output_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['vidID', 'motion_estimate'])
    for result in results:
      writer.writerow(result)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Estimate values from mp4 files.")
  parser.add_argument("--dataset", type=str, help="Path to the dataset directory containing mp4 files.")
  parser.add_argument("--estimator-cfg", default="sparse_OF", type=str, help="Either string with est. class name or .json file with 'target' and 'params' entries")
  parser.add_argument("--output", default="./estimates.csv", type=str, help="Where to write estimates")
  parser.add_argument("--parallelism", type=int, default=multiprocessing.cpu_count(), help="Number of processes to use for parallel computation.")
  args = parser.parse_args()

  # Initialize estimator
  estimator_args = {}
  if os.path.exists(args.estimator_cfg):  # config path
    config = json.load(open(args.estimator_cfg))
    estimator_cls = eval(config['target'])
    estimator_args.update(config['params'])
  else:  # estimator cls name
    estimator_cls = eval(args.estimator_cfg)

  estimator = partial(estimator_cls, **estimator_args)

  # Get mp4s
  vids = glob.glob(os.path.join(args.dataset, "*.mp4"))[:5]

  # Compute estimates
  t0 = time.time()
  with multiprocessing.Pool(processes=args.parallelism) as pool:
    results = pool.map(partial(estimate_motion, estimator=estimator), vids)
  tf = time.time()
  print(f"Rate: {len(vids)/(tf-t0)} [vid/s]")

  # Write output
  write_to_csv(results, args.output)
