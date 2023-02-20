# Copyright (c) Meta Platforms, Inc. and affiliates.

# All rights reserved.

# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.


import os
from torchvision import datasets, transforms

from timm.data.constants import \
    IMAGENET_DEFAULT_MEAN, IMAGENET_DEFAULT_STD, IMAGENET_INCEPTION_MEAN, IMAGENET_INCEPTION_STD
from timm.data import create_transform

def build_dataset(is_train, args):
    transform = build_transform(is_train, args)

    print(f"Transform = train: {is_train}")
    if isinstance(transform, tuple):
        for trans in transform:
            print(" - - - - - - - - - - ")
            for t in trans.transforms:
                print(t)
    else:
        for t in transform.transforms:
            print(t)
    print("---------------------------")
    data_paths = ['/scratch/nsingh/imagenet', 
                '/home/scratch/datasets/imagenet',
                '/scratch_local/datasets/ImageNet2012',
                '/scratch/datasets/imagenet/']
    for data_path in data_paths:
        if os.path.exists(data_path):
            break
    data_set = 'IMNET'
    if data_set == 'CIFAR':
        dataset = datasets.CIFAR100(data_path, train=is_train, transform=transform, download=True)
        nb_classes = 100
    elif data_set == 'IMNET':
        print("reading from datapath", data_path)
        root = os.path.join(data_path, 'train' if is_train else 'val')
        dataset = datasets.ImageFolder(root, transform=transform)
        nb_classes = 1000
    # elif data_set == "image_folder":
    #     root = args.data_path if is_train else args.eval_data_path
    #     dataset = datasets.ImageFolder(root, transform=transform)
    #     nb_classes = args.nb_classes
    #     assert len(dataset.class_to_idx) == nb_classes
    else:
        raise NotImplementedError()
    print("Number of the class = %d" % nb_classes)

    return dataset, nb_classes


def build_transform(is_train, args):
    resize_im = args.input_size > 32
    imagenet_default_mean_and_std = False #args.imagenet_default_mean_and_std
    mean = [0., 0., 0.] #IMAGENET_INCEPTION_MEAN if not imagenet_default_mean_and_std else IMAGENET_DEFAULT_MEAN
    std = [1., 1., 1.] #IMAGENET_INCEPTION_STD if not imagenet_default_mean_and_std else IMAGENET_DEFAULT_STD
    transform = None
    if is_train:
        # this should always dispatch to transforms_imagenet_train
        transform = create_transform(
            input_size=args.input_size,
            is_training=True,
            color_jitter=args.color_jitter,
            auto_augment=args.aa,
            interpolation=args.train_interpolation,
            re_prob=args.reprob,
            re_mode=args.remode,
            re_count=args.recount,
            mean=mean,
            std=std,
            scale=args.scale,
            ratio=args.ratio,
            hflip=args.hflip,
            vflip=args.vflip,
            crop_pct=args.crop_pct
            )
        
        return transform
        # if not resize_im:
        # trans.append(transforms.Resize(args.input_size, interpolation=transforms.InterpolationMode.BICUBIC))
        # trans.append(transforms.RandomCrop(args.input_size, padding=4))
        # trans.append(transforms.RandomHorizontalFlip())
        # trans.append(transforms.ColorJitter())
        # trans.append(transforms.ToTensor())
        # return transforms.Compose(trans)

    t = []
    if resize_im:
        # warping (no cropping) when evaluated at 384 or larger
        if args.input_size >= 384:  
            t.append(
            transforms.Resize((args.input_size, args.input_size), 
                            interpolation=transforms.InterpolationMode.BICUBIC), 
        )
            print(f"Warping {args.input_size} size input images...")
        else:
            if args.crop_pct is None:
                args.crop_pct = 224 / 256
            size = int(args.input_size / args.crop_pct)
            t.append(
                # to maintain same ratio w.r.t. 224 images
                transforms.Resize(size, interpolation=transforms.InterpolationMode.BICUBIC),  
            )
            t.append(transforms.CenterCrop(args.input_size))

    t.append(transforms.ToTensor())
    # t.append(transforms.Normalize(mean, std))
    return transforms.Compose(t)