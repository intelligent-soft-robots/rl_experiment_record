import numpy as np




class Episode:

    def __init__(self,
                 step_attributes,
                 parameters={}):
        step_attributes = {attr:numpy.zeros((val[0],1),dtype=val[1])
                           for attr,val in step_attributes.items()}
        def step_init(step_self,**attrs):
            for key,val in attrs.items():
                setattr(step_self,key,val)
        step_attributes["__init__"]=step_init
        self.Step = type("Step",(),step_attributes)
        setattr(self.Step,"__slots__",tuple([k for k in step_attributes.keys()
                                             if k !="__init__"]))
        self.parameters = parameters
        self.steps = []

    def record(self,**attributes):
        self.steps.append(self.Step(**attributes))
        
        
        
        
