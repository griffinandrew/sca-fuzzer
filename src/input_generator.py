"""
File: Input Generation

Copyright (C) Microsoft Corporation
SPDX-License-Identifier: MIT
"""
import os
import random
import numpy as np
from abc import abstractmethod
from typing import List
from .interfaces import Input, InputTaint, InputGenerator
from .config import CONF
from .util import Logger

POW32 = pow(2, 32) 

#only upper 32 are used for the input 
UINT_MAX = pow(2, 64) - 1
UINT_MIN = 0


class InputGeneratorCommon(InputGenerator):

    def __init__(self, seed: int):
        super().__init__(seed)
        self.LOG = Logger()

    def _generate_one(self) -> Input:
        raise NotImplementedError("Genetic input generation is not implemented yet.")

    #same as other class, just at init assign seed and random inputs
    def generate(self, count: int) -> List[Input]:
        # if it's the first invocation and the seed is zero - use random seed
        if self._state == 0:
            self._state = random.randint(0, pow(2, 32) - 1)
            self.LOG.inform("input_gen", f"Setting input seed to: {self._state}")

        generated_inputs = []
        for _ in range(count):
            input_ = self._generate_one()
            generated_inputs.append(input_)
        return generated_inputs

    def extend_equivalence_classes(self, inputs: List[Input],
                                   taints: List[InputTaint]) -> List[Input]:
        """
        Produce a new sequence of random inputs, but copy the tainted values from
        the base sequence, randomly mutate the input if it is not tainted from tainted
        """
        if len(inputs) != len(taints):
            raise Exception("Error: Cannot extend inputs. "
                            "The number of taints does not match the number of inputs.")
        # this function is technically not a generation function,
        # hence it should not update the global generation seed
        initial_state = self._state

        # create inputs
        new_inputs = []
        for i, input_ in enumerate(inputs):
            taint = taints[i]
            new_input = self._generate_one() 
            for j in range(input_.data_size):
                if taint[j]:
                    new_input[j] = input_[j]
                #else:
                    #only do these mutations occasionally to cut on cost and have diversity of input
                    #perhaps this could be more sophisticated, but for now this is fine
                    #if random.randint(0, 1) == 0:
                    #t_inputs = self.get_idxs_with_taint(inputs, taints, i)
                    #if (len(t_inputs) >= 2): 
                            #mutated_input = self.mutate_improved(inputs, taints, i, t_inputs)
                elif random.randint(0, 3) == 0:
                    mutated_input = self.mutate_dumb(inputs, i)
                    new_input[j] = mutated_input

            new_inputs.append(new_input)

        self._state = initial_state
        return new_inputs

    def load(self, input_paths: List[str]) -> List[Input]:
        inputs = []
        for input_path in input_paths:
            input_ = Input()

            # check that the file is not corrupted
            size = os.path.getsize(input_path)
            if size != len(input_) * 8:
                self.LOG.error(f"Incorrect size of input `{input_path}` "
                               f"({size} B, expected {len(input_) * 8} B)")

            input_.load(input_path)
            inputs.append(input_)
        return inputs


    def get_idxs_with_taint(self, inputs: List[Input],
                        taints: List[InputTaint], idx:int) -> List[int]: #i think ret type is right?
        """
        Return an array of indices of inputs that have taints for that input
        """
        indexes = []

        input_ = inputs[idx]
        taint = taints[idx]
        for j in range(input_.data_size):
            if taint[j]:
                indexes.append(j)

        return indexes #these are the location of taints aka these r uints that are working
        #now with acquired indexes, we can mutate the input, as they r uint possibly
        # by some increment or decrement, or some other operation
        # intutuon here is that if some uint is working
        # modify it slightly and see if it still works


    def get_random_idx(self, idx: List[int]) -> int:
        """
        Return a random index that is not in the list of indices
        """
        
        #select a random tainted input to modify
        random_idx = random.randint(0, len(idx) - 1)
        return random_idx


    #def mutate(self, inputs: List[Input], taints: List[InputTaint], index_of_input: int) -> Input:
    def mutate(self, inputs: List[Input], taints: List[InputTaint], index_of_input: int) -> int: #idk about this return
        """
        Mutate operator just modifies tainted inputs `slightly`
        intuition modification of tainted inputs 
        will result in a seed that could cause more coverage
        """
        #note that these params are not used / implemented, but are here for future use
        idx = self.get_idxs_with_taint(inputs, taints, index_of_input)

        random_idx = self.get_random_idx(idx)

        #mutate the input
        input = inputs[index_of_input]

        tainted_input = input[random_idx] # this is uint64

        #deal with overflow

        #(this could be very wrong?)
        if (tainted_input) == UINT_MAX:
            tainted_input -= 1 #decrement
        elif (tainted_input) == UINT_MIN:
            tainted_input += 1
        else:
            #randomly increment or decrement
            if random.randint(0, 1) == 0:
                tainted_input += 1
            else:
                tainted_input -= 1

        return tainted_input

    # perhaps return the mutated input so that can be added to non mutated inputs


    def mutate_improved(self, inputs: List[Input], taints: List[InputTaint], index_of_input: int, tainted_idx_list: List[int]) -> Input:
        """
        Mutate operator just modifies tainted inputs `slightly`
        intuition modification of tainted inputs 
        will result in a seed that could cause more coverage
        """
        #note that these params are not used / implemented, but are here for future use
        #idx_list = self.get_idxs_with_taint(inputs, taints, index_of_input)
        idx_list = tainted_idx_list
    

        #yeah this is not a self func call tho?
        #get 2 random indexes to mutate

        if(len(idx_list) == 3):

            rd_int = random.randint(0,2) 
            if rd_int == 0:
                random_idx_1 = idx_list[0]
                random_idx_1 = idx_list[1]
            elif rd_int == 1:
                random_idx_1 = idx_list[0]
                random_idx_1 = idx_list[2]
            else:
                random_idx_1 = idx_list[1]
                random_idx_1 = idx_list[2]
                    
        if (len(idx_list) == 2):
            random_idx_1 = idx_list[0]
            random_idx_2 = idx_list[1]
        else:
            random_idx_1 = self.get_random_idx(idx_list)
            random_idx_2 = self.get_random_idx(idx_list)

        #make sure not the same index
        for count in range(7):
            if random_idx_1 == random_idx_2:
                random_idx_2 = self.get_random_idx(idx_list)
            else:
                break


        #get the input from array
        input_ = inputs[index_of_input] 
        
        #get the two tainted inputs
        tainted_input_1 = input_[random_idx_1] # this is uint64
        tainted_input_2 = input_[random_idx_2] # this is uint64 so now r u like actually gonna do something with this?

        #use that intution from observations that similar activated bits trigger similar bugs
        mutated_input = tainted_input_1 | tainted_input_2

        return mutated_input

    
    def mutate_dumb(self, inputs: List[Input], index_of_input: int) -> Input:
        """
        this just mutates 2 random inputs and doesnt account for taint
        """

        #get the input from array
        input_ = inputs[index_of_input] 

        random_idx_1 = random.randint(0,(len(input_) - 1))

        print(random_idx_1)

        random_idx_2 = random.randint(0,(len(input_) - 1))
        print(random_idx_2)
        
        #get the two tainted inputs
        #64 bit ints randomly selected, not based on taint
        tainted_input_1 = input_[random_idx_1] 
        tainted_input_2 = input_[random_idx_2] 

        #use that intution from observations that similar activated bits trigger similar bugs
        
        mutated_input = tainted_input_1 | tainted_input_2

        '''
        if random.randint(0,1) == 0:
            mutated_input = tainted_input_1 | tainted_input_2
        else:
            mutated_input = tainted_input_1 & tainted_input_2
        '''
        
        

        return mutated_input



class LegacyRandomInputGenerator(InputGeneratorCommon):
    """
    Legacy implementation. Exist only for backwards compatibility.
    NumpyRandomInputGenerator is a preferred implementation.
    Implements a simple 32-bit LCG with a=2891336453 and c=54321.
    """

    def __init__(self, seed: int):
        super().__init__(seed)
        self.input_mask = pow(2, (CONF.input_gen_entropy_bits % 33)) - 1

    def _generate_one(self) -> Input:
        input_ = Input()
        input_.seed = self._state

        randint = self._state
        for i in range(input_.data_size):
            # this weird implementation is a legacy of our old PRNG.
            # basically, it's a 32-bit PRNG, assigned to 4-byte chucks of memory
            randint = ((randint * 2891336453) % POW32 + 54321) % POW32
            masked_rvalue = (randint ^ (randint >> 16)) & self.input_mask
            masked_rvalue = masked_rvalue << 6
            input_[i] = masked_rvalue << 32

            randint = ((randint * 2891336453) % POW32 + 54321) % POW32
            masked_rvalue = (randint ^ (randint >> 16)) & self.input_mask
            masked_rvalue = masked_rvalue << 6
            input_[i] += masked_rvalue

        # again, to emulate the legacy (and kinda broken) input generator,
        # initialize only the first 32 bits of registers
        for i in range(CONF.input_register_region_size // 8):
            input_[-i - 1] = input_[-i - 1] % POW32

        self._state = randint
        return input_


class NumpyRandomInputGenerator(InputGeneratorCommon):
    """ Numpy-based implementation of the input gen """

    def __init__(self, seed: int):
        super().__init__(seed)
        self.max_input_value = pow(2, CONF.input_gen_entropy_bits)

    def _generate_one(self) -> Input:
        input_ = Input()
        input_.seed = self._state

        rng = np.random.default_rng(seed=self._state)
        data = rng.integers(self.max_input_value, size=input_.data_size, dtype=np.uint64)
        data = data << CONF.memory_access_zeroed_bits  # type: ignore
        input_[:input_.data_size] = (data << 32) + data

        self._state += 1
        return input_

    
    def mutate_improved(self, inputs: List[Input], taints: List[InputTaint], index_of_input: int, tainted_idx_list: List[int]) -> Input:
        """
        Mutate operator just modifies tainted inputs `slightly`
        intuition modification of tainted inputs 
        will result in a seed that could cause more coverage
        """
        #note that these params are not used / implemented, but are here for future use
        #idx_list = self.get_idxs_with_taint(inputs, taints, index_of_input)
        idx_list = tainted_idx_list
    

        #yeah this is not a self func call tho?
        #get 2 random indexes to mutate

        if(len(idx_list) == 3):

            rd_int = random.randint(0,2) 
            if rd_int == 0:
                random_idx_1 = idx_list[0]
                random_idx_1 = idx_list[1]
            elif rd_int == 1:
                random_idx_1 = idx_list[0]
                random_idx_1 = idx_list[2]
            else:
                random_idx_1 = idx_list[1]
                random_idx_1 = idx_list[2]
                    
        if (len(idx_list) == 2):
            random_idx_1 = idx_list[0]
            random_idx_2 = idx_list[1]
        else:
            random_idx_1 = self.get_random_idx(idx_list)
            random_idx_2 = self.get_random_idx(idx_list)

        #make sure not the same index
        for count in range(7):
            if random_idx_1 == random_idx_2:
                random_idx_2 = self.get_random_idx(idx_list)
            else:
                break


        #get the input from array
        input = inputs[index_of_input] 
        
        #get the two tainted inputs
        tainted_input_1 = input[random_idx_1] # this is uint64
        tainted_input_2 = input[random_idx_2] # this is uint64 so now r u like actually gonna do something with this?

        #use that intution from observations that similar activated bits trigger similar bugs
        mutated_input = tainted_input_1 | tainted_input_2

        #at some point this will all be 1's tho, so need to like randomly choose btw a couple

        return mutated_input


    def get_idxs_with_taint(self, inputs: List[Input], taints: List[InputTaint], idx:int) -> List[int]:
        """
        Return an array of indices of inputs that have taints for that input
        """
        indexes = []

        input_ = inputs[idx]
        taint = taints[idx]
        for j in range(input_.data_size):
            if taint[j]:
                indexes.append(j)

        return indexes

    
    def get_random_idx(self, idx: List[int]) -> int:
        """
        Return a random index that is not in the list of indices
        """
        
        #select a random tainted input to modify
        random_idx = random.randint(0, len(idx) - 1)
        return random_idx

    def mutate_dumb(self, inputs: List[Input], index_of_input: int) -> Input:
        """
        this just mutates 2 random inputs and doesnt account for taint
        """

        #get the input from array
        input_ = inputs[index_of_input] 

        random_idx_1 = random.randint(0,(len(input_) - 1))
        random_idx_2 = random.randint(0,(len(input_) - 1))
        
        #get the two tainted inputs
        #64 bit ints randomly selected, not based on taint
        tainted_input_1 = input_[random_idx_1] 
        tainted_input_2 = input_[random_idx_2] 

        #use that intution from observations that similar activated bits trigger similar bugs
        
        mutated_input = tainted_input_1 | tainted_input_2

        '''
        if random.randint(0,1) == 0:
            mutated_input = tainted_input_1 | tainted_input_2
        else:
            mutated_input = tainted_input_1 & tainted_input_2
        '''
        

        return mutated_input


