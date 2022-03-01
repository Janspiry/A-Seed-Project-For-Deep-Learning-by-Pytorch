# Pytorch Template Using DistributedDataParallel

This is a seed project for distributed pytorch training, was built to customize your network quickly. 

------
### Basic Functions

- checkpoint/resume training
- progress bar (using tqdm)
- progress logs (using logging)
- progress visualization (using tensorboard)
- finetune (partial network parameters training)
- learning rate scheduler
- random seed (reproducibility)

------
### Features

- distributed training using DistributedDataParallel
- base class for more expansibility
- `.json` config file for most parameter tuning
- support multiple networks/losses/metrics definition
- debug mode for fast test 🌟

------
### Usage

#### You Need to Know 

1. cuDNN default settings are as follows for training, which may reduce your code reproducibility! Notice it to avoid the unexpected behaviors.

```python
 torch.backends.cudnn.enabled = True
 # speed-reproducibility tradeoff https://pytorch.org/docs/stable/notes/randomness.html
 if seed >=0 and gl_seed>=0:  # slower, more reproducible
     torch.backends.cudnn.deterministic = True
     torch.backends.cudnn.benchmark = False
 else:  # faster, less reproducible, default setting
     torch.backends.cudnn.deterministic = False
     torch.backends.cudnn.benchmark = True
```

2. The project allows custom classes/functions and parameters by config file. You can define dataset/network/trainer/loss/metric by the specific format. Take the `network` as the example:

```yaml
// import Network() class from models.network.py file with args
"which_networks": {
    "name": ["models.network", "Network"],
    "args": { "init_type": "kaiming"}
},

// import mutilple Network() class from defualt file without args
"which_networks": [ 
    {"name": "Network1", args: {"init_type": "kaiming"}},
    {"name": "Network2", args: {"init_type": "kaiming"}},
],

// import Network() class from defualt file without args
"which_networks" : [
    "Network1",
    "Network2"
]

// more details can be found on More Details part and init_objs function in praser.py
```



#### Start

Run the `run.py` with your setting.

```python
python run.py
```

More choices can be found on `run.py` and `config/base.json`.


#### Customize Dataset

Dataset part decide the data need to be fed into network, you can define dataset by following steps:

1. Put your dataset under `data` folder. See `dataset.py` in this folder as an example.
2. Edit the **\[dataset\]\[train|test\]** part in `config/base.json` to import and initialize dataset. 

```yaml
"datasets": { // train or test
    "train": { 
            "which_dataset": {  // import designated dataset using args 
            "name": ["data.dataset", "Dataset"], 
            "args":{ // args to init dataset
                "data_root": "/data/jlw/datasets/comofod"
            } 
        },
        "dataloader":{
        	"validation_split": 0.1, // percent or number
            "args":{ // args to init dataloader
                "batch_size": 2, // batch size in every gpu
                "num_workers": 4,
                "shuffle": true,
                "pin_memory": true,
                "drop_last": true
            }
        }
    },
}
```

##### More details

- You can import dataset from a new file. Key `name` can be a list to show your file name and class/function name, or a single string to explain class name in default file(`data.dataset.py`). Example is as follows:

```yaml
"name": ["data.dataset", "Dataset"], // import Dataset() class from data.dataset.py
"name": "Dataset", // import Dataset() class from default file
```

- You can control and record more parameters through config file. Take `data_root`  as the example, you just need to add it in `args` dict and edit corresponding class to parse this value:

```yaml
"args":{ // args to init dataset
    "data_root": "/home/huangyecheng/dataset/cmfd/comofod"
} 
```

```python
class Dataset(data.Dataset):
	def __init__(self, data_root, phase='train', image_size=[256, 256], loader=pil_loader):
		imgs = make_dataset(data_root) # data_root value is from config file
```



#### Customize Network

Network part shows your learning network structure, you can define your network by following steps:

1. Put your network under `models` folder. See `network.py` in this folder as an example.
2. Edit the **\[model\][which_networks]** part in `config/base.json` to import and initialize your networks, and it is a list. 

```yaml
"which_networks": [ // import designated list of networks using args
    {
        "name": "Network",
        "args": { // args to init network
            "init_type": "kaiming" 
        }
    }
],
```
##### More details

- You can import networks from a new file. Key `name` can be a list to show your file name and class/function name, or a single string to explain class name in default file(`models.network.py` ). Example is as follows:

```yaml
"name": ["models.network", "Network"], // import Network() class from models.network.py
"name": "Network", // import Network() class from default file
```

- You can control and record more parameters through config file. Take `init_type`  as the example, you just need to add it in `args` dict and edit corresponding class to parse this value:

```yaml
"args": { // args to init network
    "init_type": "kaiming" 
}
```

```python
class BaseNetwork(nn.Module):
	def __init__(self, init_type='kaiming', gain=0.02):
		super(BaseNetwork, self).__init__() # init_type value is from config file
class Network(BaseNetwork):
	def __init__(self, in_channels=3, **kwargs):
    	super(Network, self).__init__(**kwargs) # get init_type value and pass it to base network
```

- You can import multiple networks. You should import the networks in config file and use it in model.

```yaml
"which_networks": [ 
    {"name": "Network1", args: {}},
    {"name": "Network2", args: {}},
],
```




#### Customize Model(Trainer)

Model part shows your training process including optimizers/losses/process control, etc.  You can define your model by following steps:

1. Put your Model under `models` folder. See `model.py` in its folder as an example.
2. Edit the **\[model\][which_model]** part in `config/base.json` to import and initialize your model.

```yaml
"which_model": { // import designated  model(trainer) using args 
    "name": ["models.model", "Model"],
    "args": { // args to init model
        "lr": 1e-4,
        "weight_decay": 0
    } 
}, 
```

##### More details

- You can import model from a new file. Key `name` can be a list to show your file name and class/function name, or a single string to explain class name in default file(`models.model.py` ). Example is as follows:

```yaml
"name": ["models.model", "Model"], // import Model() class / function(not recommend) from models.model.py (default is [models.model.py])
"name": "Model", // import Model() class from default file
```

- You can control and record more parameters through config file. Take `lr`  as the example, you just need to add it in `args` dict and edit corresponding class to parse this value:

```yaml
"args": { // args to init model
    "lr": 1e-4
} 
```

```python
class Model(BaseModel):
    def __init__(self, lr, weight_decay, **kwargs):
        super(Model, self).__init__(**kwargs) # lr value is from config file
```

##### Losses and Metrics

Losses and Metrics are defined on config file. You also can control and record more parameters through config file, please refer to above  `More details` part.

```yaml
"which_metrics": ["mae"], 
"which_losses": ["mse_loss"] 
```



After above steps, you need to rewrite several functions like  `base_model.py/model.py` for your network and dataset.

##### Init step

See `__init__()` functions as the example.

##### Training/validation step

See `train_step()/val_step()` functions as the example.

##### Checkpoint/Resume training

See `save_everything()/load_everything()` functions as the example.

##### Save Results

See `save_current_results()` functions as the example.



#### Debug mode

Sometime we hope debugging the process quickly to to ensure the whole project works, so debug mode is necessary. 

This mode will reduce the dataset size and speed up the training process. You just need to run the file with `-d` option and edit the `debug` dict in config file.

```python
python run.py -d
```

```yaml
"debug": { // args in debug mode, which will replace args in train
    "val_epoch": 1,
    "save_checkpoint_epoch": 1,
    "log_iter": 30,
    "data_len": 50 // change the size of dataloder to data_len.
}
```



#### Customize More 

You can choose the random seed,  experiment path in config file. We will add more useful basic functions with related instructions. **Welcome to more contributions for more extensive customization and code enhancements.**

------
### Todo

Here are some basic functions or examples that this repository is ready to implement:

- [x] basic dataset/dataloader with validation split
- [x] basic networks with weight initialization
- [x] basic model (trainer)
- [x] checkpoint/resume training
- [x] progress bar (using tqdm)
- [x] progress logs (using logging)
- [x] progress visualization (using tensorboard)
- [x] multi-gpu support (using DistributedDataParallel and torch.multiprocessing)
- [x] finetune (partial network parameters training)
- [x] learning rate scheduler
- [x] random seed (reproducibility)
- [ ] multiple optimizer and scheduler by config file


------
### Acknowledge

We are benefit a lot from following projects:

> 1. https://github.com/Janspiry/Image-Super-Resolution-via-Iterative-Refinement
> 2. https://github.com/researchmm/PEN-Net-for-Inpainting
> 3. https://github.com/tczhangzhi/pytorch-distributed
> 4. https://github.com/victoresque/pytorch-template