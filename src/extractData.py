import collections
import workflowUtils as wu
import semantic_version as sv
import re

def getBranchesForRole(repo, roleBranches, role):
    branchNames = []
    
    if "others" in roleBranches[role] or "all" in roleBranches[role]:
        branchNames.extend(["not"])
        if "others" in roleBranches[role]:
            for key in roleBranches:
                if roleBranches[key][0] and roleBranches[key][0] != "others":
                    branchNames.extend(roleBranches[key])
    else:
        branchNames = roleBranches[role]

    branchNames = list(set(branchNames))
    return branchNames

def branchExists(repo, branch):
    branch_names = []
    exists = False
    
    for b in repo.git.branch('-r').split('\n'):
        #branch_names.append(b)
        if "" in branch:
            exists = False
        elif "not" in branch:
            tmpBranch = branch.copy()
            tmpBranch.remove("not")
            if not any(notRel in b.split('/')[-1] for notRel in tmpBranch):
                #print("Branch found: " + b)
                exists = True
                break
        else:
            if any(rel in b.split('/')[-1] for rel in branch):
                #print("Branch found: " + b)
                exists = True
                break

    return exists

def branchNamingFraction(repo, branch, naming):

    count_ok = 0
    count_total = 0
    #print(branch)
    #print(naming)
    for b in repo.git.branch('-r').split('\n'):
        if b.lower().split('/')[-2] in naming:
            branchName = b.lower().split('/')[-2] + "-" + b.lower().split('/')[-1]
        else:
            branchName = b.lower().split('/')[-1]
        if "" in branch:
            count_total = 0
        elif "not" in branch:
            tmpBranch = branch.copy()
            tmpBranch.remove("not")
            if not any(notRel in branchName for notRel in tmpBranch):
                #print("Branch found: " + branchName)
                count_total += 1
                if any([branchName.find(name) == 0 for name in naming]):
                    #print("naming found: " + branchName)
                    count_ok += 1
        else:
            if any(rel in branchName for rel in branch):
                #print("Branch found: " + branchName)
                count_total += 1
                if any([branchName.find(name) == 0 for name in naming]):
                    #print("naming found: " + branchName)
                    count_ok += 1

    if count_total == 0:
        return 0
    else:
        return count_ok / count_total
    
def countMerges(repo, branchOrig, branchTgt):

    occurences = 0
    
    if "" in branchOrig or "" in branchTgt:
        occurences = 0
    else:
        for line in list(repo.git.log('--merges','--oneline').split('\n')):
            line = line.lower().replace("'","")
            if "merge pull request" not in line and "merge branch " in line:
                orig = line.split("merge branch ")[1].split(' ')[0].strip()
                if len(line.split("into ")) > 1:
                    target = line.split("into ")[1].strip()
                else:
                    target = ""
                if "not" in branchOrig:
                    tmpBranch = branchOrig.copy()
                    tmpBranch.remove("not")
                    if not any(notRel in orig for notRel in tmpBranch):
                        #print(orig + " - " + target)
                        if("not" in branchTgt):
                            branchTgt.remove("not")
                            if not any(notRel in target for notRel in branchTgt):
                                occurences += 1
                        else:
                            if any(rel in target for rel in branchTgt):
                                occurences += 1
                else:
                    if any(rel in orig for rel in branchOrig):
                        #print(orig + " - " + target)
                        if("not" in branchTgt):
                            branchTgt.remove("not")
                            if not any(notRel in target for notRel in branchTgt):
                                occurences += 1
                        else:
                            if any(rel in target for rel in branchTgt):
                                occurences += 1
    
    return occurences
    
def countTags(repo, branch):

    occurrences = set()
    #print(branch)
    if "" in branch:
        for line in repo.git.tag('--list').split('\n'):
            occurrences.add(line.strip())
    else:
        if "not" in branch:
            tmpBranch = branch.copy()
            tmpBranch.remove("not")
            for b in tmpBranch:
                cmd = ("git tag --no-merged origin/" + b).split()
                for line in wu.runGit(cmd, repo):
                    #print(line)
                    occurrences.add(line.strip())
        else:
            for b in branch:
                cmd = ("git tag --merged origin/" + b).split()
                for line in wu.runGit(cmd, repo):
                    #print(line)
                    occurrences.add(line.strip())
    #print(len(occurrences))
    return len(occurrences)

def countBumpVersions(repo):

    occurrences = set()
    
    for line in repo.git.log('--oneline').split('\n'):
        if "bump version" in line.lower().replace("'",""):
            occurrences.add(line.lower().strip())

    return len(occurrences)

def fracFitSemVer(repo, branch):

    count_ok = 0
    count_total = 0
    
    if "" in branch:
        countTotal = 0
    else:
        for line in repo.git.log('--oneline').split('\n'):
            if '.' in line:
                if "not" in branch:
                    tmpBranch = branch.copy()
                    tmpBranch.remove("not")
                    if "remote-tracking" not in line.lower() and not any(notRel in line.lower() for notRel in tmpBranch):
                        count_total += 1
                        #print(line)
                        version = [vers for vers in re.split('/| |-', line) if '.' in vers][-1]
                        if version[0].isdigit():
                            count_total += 1
                            #print(version)
                            if sv.validate(version):
                                count_ok += 1
                else:
                    if "remote-tracking" not in line.lower() and any(rel in line.lower() for rel in branch):
                        count_total += 1
                        #print(line)
                        version = [vers for vers in re.split('/| |-', line) if '.' in vers][-1]
                        if version[0].isdigit():
                            count_total += 1
                            #print(version)
                            if sv.validate(version):
                                count_ok += 1
    
    if count_total == 0:
        return 0
    else:
        return count_ok / count_total
        
def fracFitPullRequests(repo, branch):

    features = set()
    pull_requests = set()
    
    for b in range(0, len(branch)):
        if branch[b] != "not":
            branch[b] = branch[b] + "/"
    
    if "" not in branch:
        for line in repo.git.log('--merges','--oneline').split('\n'):
            line = line.lower().replace("'","")
            if "not" in branch:
                tmpBranch = branch.copy()
                tmpBranch.remove("not")
                if not any(notRel in line for notRel in tmpBranch) and "merge branch" in line and "merge pull request" not in line and (" into " in line or " of " in line):
                    if " into " in line:
                        target = line.split("into ")[1].split('/')[-1].strip()
                    elif " of " in line:
                        target = line.split("of ")[1].split('/')[-1].strip()
                    features.add(target)
                if "merge pull request" in line and not any(notRel in line for notRel in tmpBranch):
                    target = line.split("from ")[1].split('/')[-1].strip()
                    features.add(target)
                    pull_requests.add(target)
            else:
                if any(rel in line.lower() for rel in branch) and "merge branch" in line and "merge pull request" not in line and (" into " in line or " of " in line):
                    if " into " in line:
                        target = line.split("into ")[1].split('/')[-1].strip()
                    elif " of " in line:
                        target = line.split("of ")[1].split('/')[-1].strip()
                    features.add(target)
                if "merge pull request" in line.lower() and any(rel in line.lower() for rel in branch):
                    target = line.split("from ")[1].split('/')[-1].strip()
                    features.add(target)
                    pull_requests.add(target)
    #print(features)
    #print("features: " + str(len(features)))
    #print(pull_requests)
    #print("pull_requests: " + str(len(pull_requests)))
    if len(features) > 0:
        return (abs(len(pull_requests) - len(features.difference(pull_requests)))) / len(features)
    else:
        return 0

def fracFitDailyMerges(repo, branch, freqThreshold):

    merges = []
    freqOk = 0

    if "" not in branch:
        for line in list(repo.git.log('--merges','--format="%cd %s"','--date=short').split('\n')):        
            line = line.lower().replace("'","")
            if "merge branch " in line:
                orig = line.split("merge branch ")[1].split(' ')[0].strip()
            else:
                orig = ""
            if "not" in branch:
                tmpBranch = branch.copy()
                tmpBranch.remove("not")
                if "bump version" not in line and "remote-tracking" not in line and not any(notRel in orig for notRel in tmpBranch):
                    merges.append(line.split(' ')[0])
            else:
                if "bump version" not in line and "remote-tracking" not in line and any(rel in orig for rel in branch):
                    merges.append(line.split(' ')[0])
        freqMerges = collections.Counter(merges).values()
        
        for freq in freqMerges:
            if freq >= freqThreshold:
                freqOk += 1
    #print(merges)
    #print(len(merges))
    if len(freqMerges) > 0:
        return (freqOk / len(freqMerges))
    else:
        return 0

def fracFitIntegration(repo, branchOrig, branchTgt, upstream):

    countOk = 0
    countTotal = 0
    
    #print(branchOrig)
    #print(branchTgt)
    if "" in branchOrig or "" in branchTgt:
        countTotal = 0
    else:
        for line in list(repo.git.log('--merges','--oneline').split('\n')):
            line = line.lower().replace("'","")
            if "merge pull request" not in line and "merge branch " in line:
                orig = line.split("merge branch ")[1].split(' ')[0].strip()
                if len(line.split("into ")) > 1:
                    target = line.split("into ")[1].strip()
                else:
                    target = orig
                if "not" in branchOrig:
                    tmpBranch = branchOrig.copy()
                    tmpBranch.remove("not")
                    if not any(notRel in orig for notRel in tmpBranch):
                        #print("not total: " + orig + " - " + target)
                        countTotal += 1
                        if("not" in branchTgt):
                            tmpBranch = branchTgt.copy()
                            tmpBranch.remove("not")
                            #print(tmpBranch)
                            if not any(notRel in target for notRel in tmpBranch):
                                #print("not orig: " + orig + " - " + target)
                                countOk += 1
                        else:
                            if any(rel in target for rel in branchTgt):
                                #print(orig + " - " + target)
                                countOk += 1
                    else:
                        if("not" in branchTgt):
                            tmpBranch = branchTgt.copy()
                            tmpBranch.remove("not")
                            #print(tmpBranch)
                            if not any(notRel in target for notRel in tmpBranch):
                                #print("total not orig: " + orig + " - " + target)
                                countTotal += 1
                        else:
                            if any(rel in target for rel in branchTgt):
                                #print(orig + " - " + target)
                                countTotal += 1
                else:
                    if any(rel in orig for rel in branchOrig):
                        #print("total: " + orig + " - " + target)
                        countTotal += 1
                        if("not" in branchTgt):
                            tmpBranch = branchTgt.copy()
                            tmpBranch.remove("not")
                            #print(tmpBranch)
                            if not any(notRel in target for notRel in tmpBranch):
                                #print("not target: " + orig + " - " + target)
                                countOk += 1
                        else:
                            if any(rel in target for rel in branchTgt):
                                #print(orig + " - " + target)
                                countOk += 1
                    else:
                        if("not" in branchTgt):
                            tmpBranch = branchTgt.copy()
                            tmpBranch.remove("not")
                            #print(tmpBranch)
                            if not any(notRel in target for notRel in tmpBranch):
                                #print("total not target: " + orig + " - " + target)
                                countTotal += 1
                        else:
                            if any(rel in target for rel in branchTgt):
                                #print(orig + " - " + target)
                                countTotal += 1
    
    #print(str(countOk) + " - " + str(countTotal))
    if countTotal > 0:
        return (countOk / countTotal)
    else:
        return 0