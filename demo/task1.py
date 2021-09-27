from tqdm import tqdm
import time

if __name__ == "__main__":
    print("Task1 started")
    with tqdm(range(60), desc="task1") as t:
        for i in t:
            t.set_postfix({"i": i})
            time.sleep(0.1)
    print("Task1 end")
