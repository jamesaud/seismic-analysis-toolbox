import asyncio
import time
from functools import wraps
from obspy.clients.fdsn.header import FDSNNoDataException, FDSNException
from obspy.clients.fdsn import Client
from typing import List
from .helpers import slide


class AsyncClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = asyncio.get_event_loop()

    async def async_get_waveforms(self, *args, **kwargs):
        """
        Get waveforms asyncronously
        @param *args, **kwargs: the arguments passed to Client.get_waveforms
        @return: future
        """

        # kwargs can't be passed to loop.run_in_executor, so create a wrapper function.
        @wraps(self.get_waveforms)
        def call_with_kwargs(*args):
            return self.get_waveforms(*args, **kwargs)

        future = self.loop.run_in_executor(None, call_with_kwargs, *args)
        return await future

    def _get_batch(self, batch: List, bulk_kwargs: dict):
        """
        Retrieves a batch of waveforms by calling 'get_waveforms' for each list of args in the batch
        @param batch: list[list],each sublist is arguments to be passed to get_waveforms
        @param bulk_kwargs: keyword arguments to pass the get_waveforms function. Will be applied to every batch.
        """
        tasks = [self.async_get_waveforms(*data, **bulk_kwargs) for data in batch]  # List of Asyncio Tasks
        results = self.loop.run_until_complete(asyncio.gather(*tasks))  # Blocks until finished
        return results

    def get_waveforms_bulk(self, bulk: List[List], batch_size=10, separation=1, bulk_kwargs=None, skip_errors=True):
        """
        Gets waveforms in a bulk asynchronously.
        @param bulk: List[List], data to pass get_waveforms like at - https://docs.obspy.org/packages/autogen/obspy.clients.fdsn.client.Client.get_waveforms_bulk.html
        @param batch_size: how many simultaneous requests are sent at one. Keep this number < 10
        @param bulk_kwargs: dict, kwargs to pass to each get_waveforms request because you can't store them in the bulk list.
        @param skip_errors: boolean, if False raises FSDN error if the server is missing a waveform
        @return: List[Stream], a list of the waveforms
        """
        if batch_size > 10: raise ValueError("Batch size too high, could overload server.")

        waveforms = []
        bulk_kwargs = bulk_kwargs or {}

        generate_waveforms = self.yield_waveforms_bulk(bulk, batch_size, separation, bulk_kwargs, skip_errors)

        for i, result in enumerate(generate_waveforms):
            waveforms.extend(result)
            print(f"\rGot batch {i+1}: {len(waveforms)}/{len(bulk)}", end="")

        print("\nDone.")
        return waveforms

    def yield_waveforms_bulk(self, bulk, batch_size=10, separation=1, bulk_kwargs=None, skip_errors=True):
        """
        Yields a list of streams of size batch_size. Each call to the generator makes another call to the server.
        This way you can be more strategic about how you get your data, hold it in memory, etc.
        @yield: List[Stream]
        """
        bulk_kwargs = bulk_kwargs or {}

        if batch_size > 10:
            raise ValueError("Batch size too high, could overload server.")

        for i, batch in enumerate(slide(bulk, batch_size)):
            try:
                yield self._get_batch(batch, bulk_kwargs)
            except FDSNNoDataException as e:
                if skip_errors:
                    print(f"Skipping batch {i} FDSNNoDataException")
                    continue
                raise e
            except FDSNException as e:
                if skip_errors:
                    print("FDSN Exception: ", e)
                    continue
                raise e
            finally:
                time.sleep(separation)  # Prevent overloading the server