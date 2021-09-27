from tqdm import tqdm
import time

if __name__ == "__main__":
    print("Task2 started")
    with tqdm(range(120), desc="task2") as t:
        for i in t:
            t.set_postfix({"i": i})
            time.sleep(0.1)
    print("Task2 end")
