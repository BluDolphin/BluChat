import asyncio  # async event loop primitives
import random  # random delays to simulate variable work
import time  # for simulating additional processing time in callback

def sub_work(item_id): # synchronous sub-worker function
    print(f" Sub-work {item_id} complete") # indicate sub-task start time.sleep(random.randint(1, 3)) # simulate work with sleep print(f" Sub-work {item_id} done") # indicate sub-task completion
    
async def work(item_id):  # async worker that does simple work
    print(f"Start {item_id}")  # indicate task start
    await asyncio.sleep(random.randint(1, 5))  # simulate variable-duration work
    sub_work(item_id) # call the synchronous sub-worker
    return f"Result {item_id}"  # return task result


async def main():  # main coroutine that schedules tasks
    tasks = []  # list to keep references to running tasks

    for i in range(5):  # schedule five tasks, one per loop
        print(f"Schedule {i}")  # log scheduling action
        t = asyncio.create_task(work(i))  # start the worker as a background task

        def on_done(task, a=i):  # callback run when task completes
            if task.exception():  # check for errors
                print(f"Task {a} error:", task.exception())  # print exception
            else:
                print("Handled:", task.result())  # print successful result
                for i in range(5):
                    time.sleep(1)  # simulate additional processing time
                    print(i)
                    
        t.add_done_callback(on_done)  # attach the completion callback
        tasks.append(t)  # remember the task so we can await it later
        await asyncio.sleep(1)  # stagger task starts by one second

    await asyncio.gather(*tasks, return_exceptions=True)  # wait for all tasks to finish


asyncio.run(main())  # start the asyncio event loop and run `main`
