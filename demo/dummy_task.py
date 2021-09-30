import argparse
import time

from tqdm import tqdm

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='dummy task')
    parser.add_argument('-t', '--time', type=int, default=6, help='seconds')
    args = parser.parse_args()

    print(f'{args.time}s task started')
    with tqdm(range(args.time * 10), desc='task1') as t:
        for i in t:
            t.set_postfix({'i': i})
            time.sleep(0.1)
    print('Task1 end')
