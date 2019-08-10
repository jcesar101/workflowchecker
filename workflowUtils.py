import csv
import subprocess
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

def runGit(gitCmd, repo):    
    p = subprocess.Popen(gitCmd, cwd=repo.working_dir, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b'')

def saveRules(ruleValues, repositories, rules, fileNamePrefix, timestamp):
    uniqueRules = getUniqueRules(rules)
    fields = ["wfEval", "wfRepo", "repo"]
    fields.extend(uniqueRules)

    try:
        with open(fileNamePrefix + timestamp + ".csv", 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for wfEval,wfEvalData in ruleValues.items():
                row = {'wfEval': wfEval}
                for wfRepo, wfRepoData in wfEvalData.items():
                    row = {'wfRepo': wfRepo}
                    for repo, repoData in wfRepoData.items():
                        row = {'wfEval': wfEval, 'wfRepo': wfRepo, 'repo': repo}
                        row.update(repoData)
                        writer.writerow(row)
    except IOError as e:
        print("I/O error: " + str(e)) 

def saveFitness(fitness, repositories, fileNamePrefix, timestamp):
    if "fitness" in fileNamePrefix:
        fields = ['workflow']
        for wf in repositories.keys():
            for repo in repositories[wf]:
                fields.append(repo)
    elif "avgFitness" in fileNamePrefix:
        fields = ['workflow']
        for reposWf in repositories.keys():
            fields.append(reposWf)

    try:
        with open(fileNamePrefix + timestamp + ".csv", 'w', newline='') as f:
            w = csv.DictWriter(f, fields)
            w.writeheader()
            for key,val in sorted(fitness.items()):
                row = {'workflow': key}
                row.update(val)
                w.writerow(row)
    except IOError as e:
        print("I/O error: " + str(e))
    
def plotFitness(fitness, avgFitness, workflows, repositories, colorTerm, patternTerm, fileNamePrefix, timestamp):
    figFitness, ax = plt.subplots(len(workflows),1,sharex=True,squeeze=True)
    figFitness.set_size_inches(10, 10)
    figFitness.subplots_adjust(top=0.99,hspace=0.0)
    plt.rc('font', size = 10)
    plt.rc('font', weight = 'bold')
    plt.rc('axes', labelweight = 'bold')
    plt.rc('figure', titlesize = 14)

    for index, wf in enumerate(workflows, start=0):
        ax[index].set_ylabel(wf, fontsize = 10)
        ax[index].set_ylim(0,1)
        ax[index].grid(b=True,axis='y',linewidth=0.25)
        plt.setp(ax[index].get_xticklabels(), rotation=30, horizontalalignment='right')
        plt.setp(ax[index].get_yticklabels()[0], visible=False)    
        plt.setp(ax[index].get_yticklabels()[-1], visible=False)
        vals = ax[index].get_yticks()
        ax[index].set_yticklabels(['{:,.0%}'.format(x) for x in vals])
        ax[index].bar(*zip(*fitness[wf].items()), color = "grey")
        ax[index].bar(*zip(*avgFitness[wf].items()),color="grey",edgecolor='black',linestyle='--',linewidth=1.5,alpha=0.5)
        ax[index].xaxis.label.set_size(10)

        for r in repositories[wf]:
            ax[index].patches[((len(repositories[wf]) * workflows.index(wf)) + repositories[wf].index(r) + 1) - 1].set_facecolor(colorTerm[wf])
            ax[index].patches[((len(repositories[wf]) * workflows.index(wf)) + repositories[wf].index(r) + 1) - 1].set_hatch(patternTerm[wf])

    figFitness.savefig(fileNamePrefix + timestamp + ".png", dpi=300)

    figFitness.show

def getUniqueRules(rules):
    uniqueRules = set()
    
    for wf in rules.keys():
        for r in rules[wf]:
            uniqueRules.add(r)

    return sorted(uniqueRules)