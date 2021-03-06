'''
    Skewing the datasets

        All functions return (client2set, test_set)

    How to use:
        use any of the functions, says feature_skew_noise()

        using client2dataset, te_set = feature_skew_noise('mnist',
                                                          5,
                                                          .5)
        
        we can index the **client2dataset** for corespondding dataset
            - client2dataset[0] = dataset for client 0
            - client2dataset[i] = dataset for client i
        we also have the test_set te_set
        
        then we uses loader(dataset, batch_size) to transform our
        datasets (for each client) to a dataloader

        Further steps are handed to regular Federated Learning Simulation

        Using the dictionary to acquire the dataset is all
'''

from datafiles.preprocess import preprocess
import numpy.random as random
import numpy as np

def feature_skew_noise(dataset_name,
                       nclient,
                       noise_std=.5,):
    '''
        Feature skew, adding random gaussian noise to the input
        skewing level controlled by noise standard deviation (min: 0, max: 1)
    '''
    te_set = None
    client2dataset = []
    for i in range(nclient):
        noise = True if random.randint(1, 10000) % 2 else False
        tr_s, te_s = preprocess(dataset_name=dataset_name,
                                noise=noise,
                                noise_std=noise_std)
        client2dataset.append(tr_s)
        if i == 0:
            te_set = te_s
    return client2dataset, te_set


def feature_skew_filter(dataset_name,
                        nclient,
                        filter_sz=3,):
    '''
        Feature skew, using filters to filter the dataset, 
        skewing level controlled by filter size (min: 1, max: 5)
    '''
    te_set = None
    client2dataset = []
    for i in range(nclient):
        filter = True if random.randint(1, 10000) % 2 else False
        tr_s, te_s = preprocess(dataset_name=dataset_name,
                                filter=filter,
                                filter_sz=filter_sz)
        client2dataset.append(tr_s)
        if i == 0:
            te_set = te_s
    return client2dataset, te_set


def quantity_skew(dataset_name,
                  nclient,
                  alpha=0.5):
    '''
        Dirichlet distribution, to nclient
    '''
    client2dataset = []

    tr_set, te_set = preprocess(dataset_name)
    nsample = tr_set.y.shape[0]

    indices = random.permutation(nsample)

    # normally the batchsize is 32, we want every client to have at least 32 samples
    minval = float('-inf')
    while minval < 32:
        prop = random.dirichlet([alpha] * nclient)
        prop = prop / prop.sum()
        minval = np.min(prop * len(indices))
    prop = (np.cumsum(prop) * len(indices)).astype(int)[:-1]

    indices = np.split(indices, prop)

    for i in range(nclient):
        tr_set, _ = preprocess(dataset_name=dataset_name,
                               indices=indices[i])
        client2dataset.append(tr_set)
    
    for i in range(nclient):
        print(f'Client{i} has {len(client2dataset[i])} samples')
    
    print(f"Done skewing [{dataset_name}]")

    return client2dataset, te_set
    

# each client holds some labels, following dirichlet dist.
def label_skew_across_labels(dataset_name, nclient, nlabel=10, alpha=0.5, overlap=True):
    client2dataset = []

    TR_set, te_set = preprocess(dataset_name)

    nsample = TR_set.y.shape[0]
    labels = random.permutation(nlabel)
    indices = [i for i in range(nsample)]

    minval = float('-inf')
    maxval = float('-inf')
    while minval < 1 or \
          maxval < nlabel // 2:
        # each client must have at least 1 labels
        prop = random.dirichlet([alpha] * nclient)
        minval = np.min(prop * nlabel)
        maxval = np.max(prop * nlabel)
    
    prop = np.cumsum(prop * nlabel).astype(int)[:-1]

    labels = np.split(labels, prop)

    if overlap:
        # print("overlap")
        # make label distributions overlap a bit
        redistribute = nlabel // 2
        for _ in range(redistribute):
            victim_client = random.randint(0, len(labels))
            victim_label = random.randint(0, len(labels[victim_client]))

            # select a client other than the victim
            lucky_client = victim_client
            while lucky_client == victim_client:
                lucky_client = random.randint(0, len(labels))
            
            # print(f"{victim_client}->{lucky_client}: {labels[victim_client][victim_label]}")
            
            if victim_label in labels[lucky_client]:
                pass
            else:
                # put that lucky label in it
                labels[lucky_client] = np.append(labels[lucky_client], labels[victim_client][victim_label])

    for client in range(nclient):
        label_for_client = labels[client]

        # print(label_for_client)
        indices = []
        for lb in label_for_client:
            indices.extend(np.where(TR_set.y == lb)[0])

        tr_set, _ = preprocess(dataset_name=dataset_name,
                               indices=indices)
        client2dataset.append(tr_set)
    
    return client2dataset, te_set
    
#
# courtesy to github repo: NIID_Bench utils.py, partially reference the code
#   # see here: https://github.com/Xtra-Computing/NIID-Bench/blob/a4d420297ac7811436719e3bec0347d15e5e8674/utils.py
#
# for each label, each clients hold a certain # of samples, following dirichlet dist.
def label_skew_by_within_labels(dataset_name, nclient, nlabel=10, alpha=.5):
    client2dataset = []

    tr_set, te_set = preprocess(dataset_name)

    nsample = tr_set.y.shape[0]
    indices = [i for i in range(nsample)]

    # we first generate client[i] has labels [0, 3, 5, ...] in **label[i] = its label list**
    minval = float('-inf')
    label_distribution = None
    while minval < 32:
        label_distribution = [[] for _ in range(nclient)]
        for lb in range(nlabel):
            # indices: indices of label i in tr_set
            indices = np.where(tr_set.y == lb)[0] # indices of samples, where label is k
            random.shuffle(indices)

            # now we split the indices according to dirichlet distribution
            prop = random.dirichlet([alpha] * nclient)
            # balancing
            prop = np.array([p * (len(distribution_to_i) < nsample / nclient) for p, distribution_to_i in zip(prop, label_distribution)])
            prop /= prop.sum()
            prop = (np.cumsum(prop) * len(indices)).astype(int)[:-1]
            
            label_distribution = [idx_j + idx.tolist() for idx_j, idx in zip(label_distribution, np.split(indices, prop))]

            minval = min([len(distribution_to_i) for distribution_to_i in label_distribution])
    
    for client in range(nclient):
        tr_set, _ = preprocess(dataset_name=dataset_name,
                               indices=label_distribution[client])
        client2dataset.append(tr_set)
    
    return client2dataset, te_set
 
def prepare_data(args):
    train_loaders = []
    test_loaders  = []
    tr_sets, te_set = [],[]
        
    if args.skew == 'none':
        tr_sets, te_set = feature_skew_noise(args.dataset, args.nclient, 0)
    elif args.skew == 'quantity':
        tr_sets, te_set = quantity_skew(args.dataset, args.nclient, args.Di_alpha)
    elif args.skew == 'feat_noise':
        tr_sets, te_set = feature_skew_noise(args.dataset, args.nclient, args.noise_std)
    elif args.skew == 'feat_filter':
        tr_sets, te_set = feature_skew_filter(args.dataset, args.nclient, args.filter_sz)
    elif args.skew == 'label_across':
        tr_sets, te_set = label_skew_across_labels(args.dataset, args.nclient, args.nlabel, args.Di_alpha, args.overlap)
    elif args.skew == 'label_within':
        tr_sets, te_set = label_skew_by_within_labels(args.dataset, args.nclient, args.nlabel, args.Di_alpha)
    else:
        raise ValueError("UNDEFINED SKEW")

    for tr_s in tr_sets:
        tr_l = dset2loader(tr_s,args.batch_size)
        te_l = dset2loader(te_set,args.batch_size)
        train_loaders.append(tr_l)
        test_loaders.append(te_l)
    

    return train_loaders, test_loaders