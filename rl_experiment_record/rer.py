import h5py
import numpy as np


def _get_numpy_array(step_attributes,
                     max_nb_steps):
    shape = (sum(step_attributes.values()),max_nb_steps)
    return np.zeros(shape)


class _DataBuffer:

    '''
    Encapsulate a numpy array and does
    dynamic allocation, if necessary
    '''

    def __init__(self,
                 shape):
        '''
        shape : max number of step * values per steps
        '''
        self._shape = shape
        self._data = np.empty(shape)
        # if self._index goes beyond _max_items,
        # _data will resize to 2*_max_items.
        self._index = 0
        self._max_items = shape[0]

    def clear(self):
        '''
        reset the buffer
        '''
        self._index = 0
        
    def add(self,data):
        '''
        adds a row of value, performs dynamic
        allocation if required
        '''
        # we are supposed to add only a row at a time
        assert(data.shape == (1,self._shape[1]))
        # dynamic allocation if required
        if self._index==self._max_item:
            supp = np.empty(self._shape)
            self._data = np.concatenate((self._data,supp))
            self._max_items *= 2
        self._values[self._index,:]=data
        self._index+=1

    def get(self):
        '''
        returns a view of the current data,
        i.e. shape self._index,self.shape[1]
        '''
        return self._data[:self.shape[1]]
        
        
class _Episode:

    def __init__(self,
                 step_attributes,
                 parameters,
                 data_buffer):

        # resetting the data buffer
        data_buffer.clear()
        self._data_buffer = data_buffer
    
        # parameters are the "attributes" of the episode
        # e.g. episode name, episode date, whatever
        self.parameters = parameters

        # remembering the order of the step attributes
        self.attributes = list(step_attributes.keys())
        # remembering the dimensions of each attributes
        self.dims = [step_attributes[attr] for attr in self.attributes]
        # remembering the total size of a step
        self.total_dim = sum(self.dims)
        
        self.row = np.empty((1,self.total_dim))
        
    def record_step(self,**attributes):

        # filling row with values of attributes
        # (np.nan for non specified attributes)
        def _set_values(values,index,attr,dim,attributes):
            try:
                v = attributes[attr]
            except:
                v = [np.nan]*dim
            values_[index:index+dim]=v
        total_index = 0
        for index,(attr,dim) in enumerate(zip(self.attributes,self.dims)):
            _set_values(self.row,total_index,attr,dim,attributes)
            total_index += dim
            
        # setting the row values to the data buffer
        # (i.e. on row per step in the data buffer)
        self._data_buffer.add(self.row)
            
        # checking all passed keyword arguments are valid
        # (i.e. ok for the constructor of Step)
        self.asserts(all([attr in self.Step.__slots__
                          for attr in attributes.keys()]))
        
        # appending an instance of Step to steps
        self.steps.append(self.Step(**attributes))
        

class Experiment:

        def __init__(self,
                     experiment_id,
                     h5p_path,
                     step_attributes,
                     max_nb_steps=10000)

        # saving step attributes names and sizes
        self._step_attributes = step_attributes
        
        # creating a new class "Step" with attributes the
        # keys of step_attributes and values numpy arrays of
        # size the items of step_attributes.
        # The constructor of Step will take keyword arguments,
        # one per attribute.
        step_attributes = {attr:numpy.zeros((val[0],1),dtype=val[1])
                           for attr,val in step_attributes.items()}
        def step_init(step_self,**attrs):
            for key,val in attrs.items():
                setattr(step_self,key,val)
        step_attributes["__init__"]=step_init
        self.Step = type("Step",(),step_attributes)
        setattr(self.Step,"__slots__",tuple([k for k in step_attributes.keys()
                                             if k !="__init__"]))

        
        # the h5py file in which the "results" of the experiment
        # are to be recorded
        self.f = h5py.File(h5p_path,"a")

        # the corresponding group (directory) in the file 
        self.experiment_group = f.create_group(experiment_id)

        # each episode of the experiment will have its own
        # group. Initializing here the current episode
        self.episode_group = None
        self.episode = None

        
    def _record_episode(self):

        # currently, the episode is saved in the memory
        # as a list of instances of Step.
        # converting this into numpy arrays that can
        # be saved in the h5 file
        
        nb_steps = len(self.episode.steps)

        # values is the numpy matrix that will encapsulate all the
        # data.
        values = np.zeros()
        
        values = {key:np.zeros(value,nb_steps)
                  for key,value in self._step_attributes.items()}
        
        for step in self.episode.steps:
            for attr in attributes:
                locals_[param][step] = np.array(getattr(step,param))
            self.episode_group.create_dataset(param,locals_.shape,dtype=locals_.dtype)
        
        self.episode_group.attrs["reward"]=self.episode.reward

        self.f.flush()
        
    def next_episode(self,episode_id):
        if self.episode:
            self._record_episode()
        self.episode = Episode()
        self.episode_group = self.experiment_group.create_group(episode_id)

    def set_reward(self,reward):
        self.episode.reward = reward

    def record(self,**step_attributes)
        self.episode.record(**step_attributes)

    def close(self):
        self.f.close()

        
        
