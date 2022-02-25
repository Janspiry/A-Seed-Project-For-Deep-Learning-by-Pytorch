import numpy as np
import torch
import torch.nn as nn
from torch.optim import lr_scheduler

import logging

from .base_model import BaseModel
from . import networks
import core.util as Util
logger = logging.getLogger('base')

class Model(BaseModel):
    def name(self):
        return 'AEModel'
    def __init__(self, opt):
        super(Model, self).__init__(opt)
        
        ''' define networks, which are a list'''
        self.net = networks.define_networks(opt)[0]

        ''' define parameters, include loss, optimizers, schedulers, etc.''' 
        if self.phase != 'test':
            self.net.train()

            ''' loss, import munual loss using Util.set_device '''
            self.loss_fn = nn.L1Loss()
        
            ''' find the parameters to optimize '''
            if opt['finetune_norm']:
                for k, v in self.net.named_parameters():
                    if k.find('backbone') >= 0:
                        v.requires_grad = False
            optim_params = list(filter(lambda p: p.requires_grad, self.net.parameters()))
           
            ''' optimizers '''
            self.optimizer = torch.optim.Adam(optim_params, lr=1e-4, weight_decay=0)
            self.optimizers.append(self.optimizer)

            ''' schedulers, not sued now '''
            for optimizer in self.optimizers:
                pass
                self.schedulers.append(torch.optim.lr_scheduler.CyclicLR(
                    optimizer,
                    base_lr=1e-7,
                    max_lr=1e-4,
                    gamma=0.99994,
                    cycle_momentum=False)
                )
        ''' load pretrained models and print network '''
        self.load() 
        self.print_network()

    def set_input(self, data):
        self.input = Util.set_device(data['input']) # you must use set_device in tensor
        self.path = data['path']

    def get_image_paths(self):
        return self.path
        
    def optimize_parameters(self):
        self.optimizer.zero_grad()
        self.output = self.net(self.input)
        l_pix = self.loss_fn(self.output, self.input)
        l_pix.backward()
        self.optimizer.step()

        ''' set log '''
        self.log_dict['l_pix'] = l_pix.item()

    def test(self):
        self.net.eval()
        with torch.no_grad():
            self.output = self.net(self.input)
            l_pix = self.loss_fn(self.output, self.input)
            self.log_dict['l_pix'] = l_pix.item()
        self.net.train()

    def get_current_visuals(self):
        self.visuals_dict['input'] = self.input.detach()[0].float().cpu()
        self.visuals_dict['output'] = self.output.detach()[0].float().cpu()
        return self.visuals_dict

    def save_current_results(self):
        self.results_dict._replace(name=self.path)
        self.results_dict._replace(result=self.output)
        return self.results_dict._asdict()

    def load(self):
        load_path = self.opt['path']['resume_state']
        self.load_network(load_path, network=self.net, network_label="net")
        self.resume_training(load_path)
    
    def save(self, total_iters, total_epoch):
        if self.opt['global_rank']!=0:
            return
        self.save_network(network=self.net, network_label='net', total_iters=total_iters)
        self.save_training_state(total_epoch, total_iters)

