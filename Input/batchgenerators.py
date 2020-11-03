# -*- coding: utf-8 -*-

import numpy as np

from Input import multistreamcache
from Input import multistreamworkers
#import Utils


#N.B. needs reimplementation

class BatchGen_Paired:
    '''
    Generates three matched batches of mixture, speech and background noise, all in the shape [batch_size, freqs, time, 1]
    so that the ground truth output for mixture[x,:,:,:] is speech[x,:,:,:] and noise[x,:,:,:] respectively.
    '''
    def __init__(self,
                 model_config,
                 dataset,
                 input_shape,
                 output_shape,
                 padding_duration):

        self.options = model_config.copy() # Create local copy
        self.options["file_list"] = dataset
        self.options["separate_cache"] = True
        self.options["input_shape"] = input_shape
        self.options["output_shape"] = output_shape
        self.options["padding_duration"] = padding_duration
        self.options["pad_frames"] = (input_shape[1] - output_shape[1]) / 2

        # Internal Data Structures
        self.cache = multistreamcache.MultistreamCache(multistreamworkers.MultistreamWorker_GetSpectrogram.run,
                                                       self.options)

    def start_workers(self):
        '''
        Start all the workers associated with this batch generator.
        '''
        self.cache.start_workers()

    def stop_workers(self):
        '''
        Stop all the workers associated with this batch generator.
        '''
        self.cache.stop_workers()

    def get_batch(self):
        '''
        Generates three batch of examples by randomly extracting patches from the cache, and padding to fit the required input shapes.
        :return: Three matched batches with shape [batch_size, frequencies, time_frames, 1]  in a list [mix, noise, speech]
        '''

        # Updating the Cache once per batch generation
        self.cache.update_cache_from_queue()

        input_mix = np.zeros(self.options["input_shape"], dtype=np.float32) # Preallocate batch
        sources = [np.zeros(self.options["output_shape"], dtype=np.float32) for _ in range(self.options["num_sources"])]

        # Decide which items to read from cache. block calls to np.random.randint are faster
        idx_cache_items = np.random.randint(0, self.options["cache_size"], size=self.options["batch_size"])

        # Iterate over samples, perform zero-padding in time domain if example is too short, and zero-pad frequencies
        for sample_num in range(self.options["batch_size"]): # For each sample consisting of mix, noise, speech...
            cache_item = self.cache.get_cache_item(idx_cache_items[sample_num])

            # Input Start and end index for sources
            if cache_item[1].shape[0] - self.options["num_frames"] < 0:
                print("Cache item has too few time frames!")
            start_idx_input = np.random.randint(0, cache_item[1].shape[0] - self.options["output_shape"][1] + 1)
            stop_idx_input = start_idx_input + self.options["output_shape"][1] # exclusive idx

            for i in range(self.options["num_sources"]):
                sources[i][sample_num,:,:] = cache_item[i+1][start_idx_input:stop_idx_input,:]

            # Read mixture with context
            total_padding = cache_item[0].shape[0] - cache_item[1].shape[0]
            extra_padding = total_padding - 2*self.options["pad_frames"]
            skip_pad = extra_padding // 2
            if skip_pad > 0:
                print("WARNING: Had to fix input padding by " + str(skip_pad) + " samples while creating the batch")
            assert(cache_item[0].shape[0] > 0)
            input_mix[sample_num, :, :] = cache_item[0][int(start_idx_input+skip_pad):int(stop_idx_input+skip_pad+2*self.options["pad_frames"]),:]

        return [input_mix] + sources
