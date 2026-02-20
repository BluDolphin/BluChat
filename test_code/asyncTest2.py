import asyncio
import random

async def temp(i):
    print(f'temp start {i}')
    await asyncio.sleep(random.randint(1, 5))  # Simulate variable processing time
    return f'temp done {i}'
    
async def main():
    queue = asyncio.Queue()

    async def consumer():
        while True:
            item = await queue.get()
            if item is None:  # sentinel to stop
                queue.task_done()
                break

            if isinstance(item, Exception):
                print('task error:', item)
            else:
                print('result:', item)
                handled = f"handled -> {item}"
                print(handled)

            queue.task_done()

    consumer_task = asyncio.create_task(consumer())

    tasks = []
    for i in range(5):
        print('1')
        t = asyncio.create_task(temp(i))

        # push result into queue as soon as the task completes
        def _done_cb(task, q=queue):
            try:
                res = task.result()
            except Exception as e:
                q.put_nowait(e)
            else:
                q.put_nowait(res)

        t.add_done_callback(_done_cb)
        tasks.append(t)
        await asyncio.sleep(1)

    # wait for all tasks to finish, then signal the consumer to stop
    await asyncio.gather(*tasks, return_exceptions=True)
    await queue.put(None)
    await consumer_task
            
asyncio.run(main())
