import asyncio
import random

async def temp(i):
    print(f'temp start {i}')
    await asyncio.sleep(random.randint(1, 5))  # Simulate variable processing time
    return f'temp done {i}'
    
async def main():
    tasks = []
    for i in range(5):
        print('1')
        tasks.append(asyncio.create_task(temp(i)))
        await asyncio.sleep(1)

    # Process results as each task finishes and continue main with the returned value
    for finished in asyncio.as_completed(tasks):
        try:
            result = await finished
            print('result:', result)
            # continue main's logic immediately using the returned value
            handled = f"handled -> {result}"
            print(handled)

        except Exception as e:
            print('task error:', e)
            
asyncio.run(main())
