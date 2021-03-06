import argparse
import os
import matplotlib.pyplot as plt

# use this to parse train_loss, other loss is meaning less to be analyzed
def parse_dict(logpath, keyword):
    '''
        Args:
            - logpath: the path of logfile
            - keyword: the keyword to find in the file

        Returns the parsed dictionary
    '''
    d = {}
    with open(logpath, mode='r') as f:
        rows = f.readlines()
        target_word = keyword
        for row in rows:
            pos = row.find(target_word)  # row must have word "Train Loss: "
            if pos != -1:
                # find dataset name, as key
                dataset_name = row[:row.find("|")].strip()
                if dataset_name not in d:
                    d[dataset_name] = []

                pos += len(target_word)
                row = row[pos:]  # strip all the things before the loss

                spacepos = row.find(' ')  # find the space after the number
                if spacepos != -1:
                    row = row[:spacepos]  # strip all things after the loss

                loss = float(row)
                d[dataset_name].append(loss)
    return d

def average_loss_history(loss_history_dict):
    keys = list(loss_history_dict.keys())
    nhist = len(loss_history_dict[keys[0]])
    hist = []
    for i in range(nhist):
        val = 0
        for key in keys:
            val += loss_history_dict[key][i]
        val /= len(keys)
        hist.append(val)
    return hist

def draw_plot(x_hist,
              y_hists,
              labels,
              title,
              x_label,
              y_label,
              name):
    plt.cla()  # clean all plots before
    for i, y_hist in enumerate(y_hists):
        plt.plot(x_hist, y_hist, label=labels[i])
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.savefig(os.path.join('./figures', name))

folder = 'logs/DigitModel'
datasets = ['mnist', 'kmnist', 'svhn', 'cifar10']
skews = ['none', 'quantity', 'feat_filter', 'feat_noise', 'label_across', 'label_within']
# skews = ['quantity', 'feat_filter', 'feat_noise', 'label_across', 'label_within']
nclient = '4'

def draw_per_dataset_per_skew():
    for dataset in datasets:
        for skew in skews:
            logname_fedbn = f'fedbn_{dataset}_{skew}_{nclient}_test.log'
            logname_fedprox = f'fedprox_{dataset}_{skew}_{nclient}_test.log'
            logname_fedavg = f'fedavg_{dataset}_{skew}_{nclient}_test.log'
            logname_moon = f'moon_{dataset}_{skew}_{nclient}_test.log'
            logname_pfedme = f'pfedme_{dataset}_{skew}_{nclient}_test.log'
            logname_perfedavg = f'perfedavg_{dataset}_{skew}_{nclient}_test.log'

            logfile_fedbn = os.path.join(folder, logname_fedbn)
            logfile_fedprox = os.path.join(folder, logname_fedprox)
            logfile_fedavg = os.path.join(folder, logname_fedavg)
            logfile_moon = os.path.join(folder, logname_moon)
            logfile_pfedme = os.path.join(folder, logname_pfedme)
            logfile_perfedavg = os.path.join(folder, logname_perfedavg)

            # loss_history_{algorithm}: has key(client 0, client1, client2 and client 3)
            # we average the loss history of nclient to be our final loss history
            loss_history_fedbn = parse_dict(logfile_fedbn, "Train Loss: ")
            loss_history_fedbn = average_loss_history(loss_history_fedbn)
            acc_history_fedbn = parse_dict(logfile_fedbn, "Test  Acc: ")['server']

            loss_history_fedprox = parse_dict(logfile_fedprox, "Train Loss: ")
            loss_history_fedprox = average_loss_history(loss_history_fedprox)
            acc_history_fedprox = parse_dict(logfile_fedprox, "Test  Acc: ")['server']

            loss_history_fedavg = parse_dict(logfile_fedavg, "Train Loss: ")
            loss_history_fedavg = average_loss_history(loss_history_fedavg)
            acc_history_fedavg = parse_dict(logfile_fedavg, "Test  Acc: ")['server']

            # loss_history_moon = parse_dict(logfile_moon, "Train Loss: ")
            # loss_history_moon = average_loss_history(loss_history_moon)
            acc_history_moon = parse_dict(logfile_moon, "Test  Acc: ")['server']

            acc_history_pfedme = parse_dict(logfile_pfedme, "Test  Acc: ")['server']

            acc_history_perfedavg = parse_dict(logfile_perfedavg, "Test  Acc: ")['server']

            print(dataset, skew)
            print(len(acc_history_fedavg), len(acc_history_fedprox), len(acc_history_fedbn), len(acc_history_moon), len(acc_history_perfedavg), len(acc_history_pfedme))
            minlen = min(len(acc_history_fedavg), len(acc_history_fedprox), len(acc_history_fedbn), len(acc_history_moon), len(acc_history_perfedavg), len(acc_history_pfedme))
            nepochs = range(1, minlen + 1)
            acc_history_fedavg = acc_history_fedavg[:minlen]
            acc_history_fedprox = acc_history_fedprox[:minlen]
            acc_history_fedbn = acc_history_fedbn[:minlen]
            acc_history_moon = acc_history_moon[:minlen]
            acc_history_perfedavg = acc_history_perfedavg[:minlen]
            acc_history_pfedme = acc_history_pfedme[:minlen]
            print(len(acc_history_fedavg), len(acc_history_fedprox), len(acc_history_fedbn), len(acc_history_moon), len(acc_history_perfedavg), len(acc_history_pfedme))
            print("")

            # draw_plot(x_hist=nepochs,
            #         y_hists=[loss_history_fedavg,
            #                 loss_history_fedprox,
            #                 loss_history_fedbn],
            #         labels=["FedAvg", "FedProx", "FedBN"],
            #         title=f"Loss History on {dataset}_{skew} {nclient} clients",
            #         x_label="Global Epochs",
            #         y_label="Loss",
            #         name=f'Loss_{dataset}_{skew}.png')

            draw_plot(x_hist=nepochs,
                      y_hists=[acc_history_fedavg,
                            acc_history_fedprox,
                            acc_history_fedbn,
                            acc_history_moon,
                            acc_history_pfedme,
                            acc_history_perfedavg,
                            ],
                    labels=["FedAvg", "FedProx", "FedBN", "MOON", "pFedMe", "perFedAvg"],
                    # labels=["FedAvg", "FedProx", "FedBN"],
                    title=f"Test Accuracy History on {dataset}_{skew} {nclient} clients",
                    x_label="Global Epochs",
                    y_label="Accuracy (%)",
                    name=os.path.join('algo_comp', f'Tacc_{dataset}_{skew}.png'))

def draw_per_dataset_per_algo():
    for dataset in datasets:
        for algo in ['fedbn', 'fedprox', 'fedavg', 'moon']:
            logname_none = f'{algo}_{dataset}_none_{nclient}_test.log'
            logname_quantity = f'{algo}_{dataset}_quantity_{nclient}_test.log'
            logname_feat_filter = f'{algo}_{dataset}_feat_filter_{nclient}_test.log'
            logname_feat_noise = f'{algo}_{dataset}_feat_noise_{nclient}_test.log'
            logname_label_across = f'{algo}_{dataset}_label_across_{nclient}_test.log'
            logname_label_within = f'{algo}_{dataset}_label_within_{nclient}_test.log'

            logfile_n = os.path.join(folder, logname_none)
            logfile_q = os.path.join(folder, logname_quantity)
            logfile_ff = os.path.join(folder, logname_feat_filter)
            logfile_fn = os.path.join(folder, logname_feat_noise)
            logfile_la = os.path.join(folder, logname_label_across)
            logfile_lw = os.path.join(folder, logname_label_within)

            acc_history_n = parse_dict(logfile_n, "Test  Acc: ")['server']
            acc_history_q = parse_dict(logfile_q, "Test  Acc: ")['server']
            acc_history_ff = parse_dict(logfile_ff, "Test  Acc: ")['server']
            acc_history_fn = parse_dict(logfile_fn, "Test  Acc: ")['server']
            acc_history_la = parse_dict(logfile_la, "Test  Acc: ")['server']
            acc_history_lw = parse_dict(logfile_lw, "Test  Acc: ")['server']

            nepochs = range(1, len(acc_history_ff) + 1)

            draw_plot(x_hist=nepochs,
                      y_hists=[acc_history_n,
                               acc_history_q,
                               acc_history_ff,
                               acc_history_fn,
                               acc_history_la,
                               acc_history_lw],
                      labels=["None", "Quantity", "Filter", "Noise", "Label_across", "Label_within"],
                      title=f"Test Accuracy History on {dataset} for {algo}",
                      x_label="Global Epochs",
                      y_label="Accuracy (%)",
                      name=os.path.join('skew_comp', f'Tacc_{algo}_{dataset}.png'))

def draw_lbfedbn():
    _skews = ['label_across', 'label_within']
    for dataset in datasets:
        for skew in _skews:
            logname_fedbn = f'fedbn_{dataset}_{skew}_{nclient}_test.log'
            logname_fedprox = f'fedprox_{dataset}_{skew}_{nclient}_test.log'
            logname_fedavg = f'fedavg_{dataset}_{skew}_{nclient}_test.log'
            logname_lbfedbn = f'fedbnLabel_{dataset}_{skew}_{nclient}_test.log'

            logfile_fedbn = os.path.join(folder, logname_fedbn)
            logfile_fedprox = os.path.join(folder, logname_fedprox)
            logfile_fedavg = os.path.join(folder, logname_fedavg)
            logfile_lbfedbn = os.path.join(folder, logname_lbfedbn)

            # loss_history_{algorithm}: has key(client 0, client1, client2 and client 3)
            # we average the loss history of nclient to be our final loss history
            loss_history_fedbn = parse_dict(logfile_fedbn, "Train Loss: ")
            loss_history_fedbn = average_loss_history(loss_history_fedbn)
            acc_history_fedbn = parse_dict(logfile_fedbn, "Test  Acc: ")['server']

            loss_history_fedprox = parse_dict(logfile_fedprox, "Train Loss: ")
            loss_history_fedprox = average_loss_history(loss_history_fedprox)
            acc_history_fedprox = parse_dict(logfile_fedprox, "Test  Acc: ")['server']

            loss_history_fedavg = parse_dict(logfile_fedavg, "Train Loss: ")
            loss_history_fedavg = average_loss_history(loss_history_fedavg)
            acc_history_fedavg = parse_dict(logfile_fedavg, "Test  Acc: ")['server']

            loss_history_lbfedbn = parse_dict(logfile_lbfedbn, "Train Loss: ")
            loss_history_lbfedbn = average_loss_history(loss_history_lbfedbn)
            acc_history_lbfedbn = parse_dict(logfile_lbfedbn, "Test  Acc: ")['server']

            nepochs = range(1, len(loss_history_fedavg) + 1)

            # draw_plot(x_hist=nepochs,
            #         y_hists=[loss_history_fedavg,
            #                 loss_history_fedprox,
            #                 loss_history_fedbn],
            #         labels=["FedAvg", "FedProx", "FedBN"],
            #         title=f"Loss History on {dataset}_{skew} {nclient} clients",
            #         x_label="Global Epochs",
            #         y_label="Loss",
            #         name=f'Loss_{dataset}_{skew}.png')

            draw_plot(x_hist=nepochs,
                    y_hists=[acc_history_fedavg,
                            acc_history_fedprox,
                            acc_history_fedbn,
                            acc_history_lbfedbn],
                    labels=["FedAvg", "FedProx", "FedBN", "LWFedBN"],
                    title=f"Test Accuracy History on {dataset}_{skew} {nclient} clients",
                    x_label="Global Epochs",
                    y_label="Accuracy (%)",
                    name=os.path.join('fedbnlabel', f'Tacc_{dataset}_{skew}.png'))

def draw_choke():
    __folder = './log_choke'
    __skews = ['feat_filter']
    __datasets = ['kmnist', 'mnist']
    for dataset in __datasets:
        for skew in __skews:
            logname_fedbn = f'fedbn_{dataset}_{skew}_{nclient}_test.log'
            logname_fedprox = f'fedprox_{dataset}_{skew}_{nclient}_test.log'
            logname_fedavg = f'fedavg_{dataset}_{skew}_{nclient}_test.log'
            logname_cavg = f'fedavgChoking_{dataset}_{skew}_{nclient}_test.log'
            logname_cprox = f'fedproxChoking_{dataset}_{skew}_{nclient}_test.log'

            logfile_fedbn = os.path.join(__folder, logname_fedbn)
            logfile_fedprox = os.path.join(__folder, logname_fedprox)
            logfile_fedavg = os.path.join(__folder, logname_fedavg)
            logfile_cavg = os.path.join(__folder, logname_cavg)
            logfile_cprox = os.path.join(__folder, logname_cprox)

            # loss_history_{algorithm}: has key(client 0, client1, client2 and client 3)
            # we average the loss history of nclient to be our final loss history
            loss_history_fedbn = parse_dict(logfile_fedbn, "Train Loss: ")
            loss_history_fedbn = average_loss_history(loss_history_fedbn)
            acc_history_fedbn = parse_dict(logfile_fedbn, "Test  Acc: ")['server']

            loss_history_fedprox = parse_dict(logfile_fedprox, "Train Loss: ")
            loss_history_fedprox = average_loss_history(loss_history_fedprox)
            acc_history_fedprox = parse_dict(logfile_fedprox, "Test  Acc: ")['server']

            loss_history_fedavg = parse_dict(logfile_fedavg, "Train Loss: ")
            loss_history_fedavg = average_loss_history(loss_history_fedavg)
            acc_history_fedavg = parse_dict(logfile_fedavg, "Test  Acc: ")['server']

            loss_history_cavg = parse_dict(logfile_cavg, "Train Loss: ")
            loss_history_cavg = average_loss_history(loss_history_cavg)
            acc_history_cavg = parse_dict(logfile_cavg, "Test  Acc: ")['server']

            loss_history_cprox = parse_dict(logfile_cprox, "Train Loss: ")
            loss_history_cprox = average_loss_history(loss_history_cprox)
            acc_history_cprox = parse_dict(logfile_cprox, "Test  Acc: ")['server']

            nepochs = range(1, len(loss_history_fedavg) + 1)

            # draw_plot(x_hist=nepochs,
            #         y_hists=[loss_history_fedavg,
            #                 loss_history_fedprox,
            #                 loss_history_fedbn],
            #         labels=["FedAvg", "FedProx", "FedBN"],
            #         title=f"Loss History on {dataset}_{skew} {nclient} clients",
            #         x_label="Global Epochs",
            #         y_label="Loss",
            #         name=f'Loss_{dataset}_{skew}.png')

            draw_plot(x_hist=nepochs,
                    y_hists=[acc_history_fedavg,
                            acc_history_fedprox,
                            acc_history_fedbn,
                            acc_history_cavg,
                            acc_history_cprox,
                            ],
                    labels=["FedAvg", "FedProx", "FedBN", "FedAvg-Choked", "FedProx-Choked"],
                    title=f"Test Accuracy History on {dataset}_{skew} {nclient} clients",
                    x_label="Global Epochs",
                    y_label="Accuracy (%)",
                    name=os.path.join('choke', f'Tacc_{dataset}_{skew}.png'))

draw_per_dataset_per_skew()
# draw_per_dataset_per_algo()
# draw_lbfedbn()
# draw_choke()