import extractData as ed

# Category 1
def rule_1_b_i_A(repo, weight, roleBranches, parameters):
    # Rule 1.b.i.A - Main branch assuming Main role

    fitness = 0
    branch = ed.getBranchesForRole(repo,roleBranches,"main")

    if ed.branchExists(repo, branch):
        fitness = 1 * weight

    return fitness

def rule_1_b_ii_B(repo, weight, roleBranches, parameters):
    # Rule 1.b.ii.B - Integration branch assuming Integration role
	
    fitness = 0
    branch = ed.getBranchesForRole(repo,roleBranches,"integration")

    if ed.branchExists(repo, branch):
        fitness = 1 * weight

    return fitness

def rule_1_c_i_A(repo, weight, roleBranches, parameters):
    # Rule 1.c.i.A - Main branch in origin

    fitness = 0
    branch = ed.getBranchesForRole(repo,roleBranches,"main")

    if ed.branchExists(repo, branch):
        fitness = 1 * weight

    return fitness

def rule_1_c_ii_A(repo, weight, roleBranches, parameters):
    # Rule 1.c.ii.A - Integration branch in origin

    fitness = 0
    branch = ed.getBranchesForRole(repo,roleBranches,"integration")

    if ed.branchExists(repo, branch):
        fitness = 1 * weight

    return fitness

# Category 2
def rule_2_a_ii_D(repo, weight, roleBranches, parameters):
    # Rule 2.a.ii.D - Integration branch created to integrate work

    mainBranch = ed.getBranchesForRole(repo,roleBranches,"main")
    integrationBranch = ed.getBranchesForRole(repo,roleBranches,"integration")

    merges_into_develop = ed.countMerges(repo, integrationBranch, ["not", mainBranch[0]])
    merges_into_master = ed.countMerges(repo, mainBranch, ["not", integrationBranch[0]])
    
    if (merges_into_develop + merges_into_master) > 0:
        fitness = (merges_into_develop/(merges_into_develop + merges_into_master)) * weight
    else:
        fitness = 0

    return fitness

def rule_2_a_v_B(repo, weight, roleBranches, parameters):
    # Rule 2.a.v.B - Fix branches created to develop fixes
    
    branch = ed.getBranchesForRole(repo,roleBranches,"fix")
    fitness = ed.fracFitPullRequests(repo, branch) * weight
    
    return fitness

# Category 3
def rule_3_a_i_J(repo, weight, roleBranches, parameters):
    # Rule 3.a.i.J - Main branch integrated as frequently as possible

    branch = ed.getBranchesForRole(repo,roleBranches,"main")
    if "freqThreshold" in parameters.keys():
        fitness = ed.fracFitDailyMerges(repo, branch, parameters["freqThreshold"]) * weight
    else:
        fitness = 0

    return fitness
    
def rule_3_a_iii_J(repo, weight, roleBranches, parameters):
    # Rule 3.a.iii.J - Change branches integrated as frequently as possible

    branch = ed.getBranchesForRole(repo,roleBranches,"change")
    if "freqThreshold" in parameters.keys():
        fitness = ed.fracFitDailyMerges(repo, branch, parameters["freqThreshold"]) * weight
    else:
        fitness = 0

    return fitness

def rule_3_a_iv_E(repo, weight, roleBranches, parameters):
    # Rule 3.a.iv.E - Release branches integrated after code review completed (pull request)

    branch = ed.getBranchesForRole(repo,roleBranches,"release")
    fitness = ed.fracFitPullRequests(repo, branch) * weight
    
    return fitness

def rule_3_a_v_E(repo, weight, roleBranches, parameters):
    # Rule 3.a.v.E - Fix branches integrated after code review completed (pull request)

    branch = ed.getBranchesForRole(repo,roleBranches,"fix")
    fitness = ed.fracFitPullRequests(repo, branch) * weight

    return fitness

def rule_3_b_iii_A(repo, weight, roleBranches, parameters):
    # Rule 3.b.iii.A - Main branch integrated into Change branches upstream

    branchOrig = ed.getBranchesForRole(repo,roleBranches,"main")
    branchTgt = ed.getBranchesForRole(repo,roleBranches,"change")
    fitness = ed.fracFitIntegration(repo, branchOrig, branchTgt, True) * weight

    return fitness

def rule_3_b_iii_B(repo, weight, roleBranches, parameters):
    # Rule 3.b.iii.B - Main branch integrated into Change branches downstream

    branchOrig = ed.getBranchesForRole(repo,roleBranches,"main")
    branchTgt = ed.getBranchesForRole(repo,roleBranches,"change")
    fitness = ed.fracFitIntegration(repo, branchOrig, branchTgt, False) * weight

    return fitness

def rule_3_d_ii_A(repo, weight, roleBranches, parameters):
    # Rule 3.d.ii.A - Change branches integrated into integration branch upstream

    branchOrig = ed.getBranchesForRole(repo,roleBranches,"change")
    branchTgt = ed.getBranchesForRole(repo,roleBranches,"integration")
    fitness = ed.fracFitIntegration(repo, branchOrig, branchTgt, True) * weight

    return fitness

def rule_3_d_iii_A(repo, weight, roleBranches, parameters):
    # Rule 3.d.iii.A - Change branches integrated into change branch upstream

    branchOrig = ed.getBranchesForRole(repo,roleBranches,"change")
    branchTgt = ed.getBranchesForRole(repo,roleBranches,"change")
    fitness = ed.fracFitIntegration(repo, branchOrig, branchTgt, True) * weight

    return fitness

def rule_3_d_iv_A(repo, weight, roleBranches, parameters):
    # Rule 3.d.iv.A - Change branches integrated into release branch upstream

    branchOrig = ed.getBranchesForRole(repo,roleBranches,"change")
    branchTgt = ed.getBranchesForRole(repo,roleBranches,"release")
    fitness = ed.fracFitIntegration(repo, branchOrig, branchTgt, True) * weight

    return fitness

def rule_3_e_i_A(repo, weight, roleBranches, parameters):
    # Rule 3.e.i.A - Release branches integrated into main branch upstream

    branchOrig = ed.getBranchesForRole(repo,roleBranches,"release")
    branchTgt = ed.getBranchesForRole(repo,roleBranches,"main")
    fitness = ed.fracFitIntegration(repo, branchOrig, branchTgt, True) * weight

    return fitness

def rule_3_e_ii_A(repo, weight, roleBranches, parameters):
    # Rule 3.e.ii.A - Release branches integrated into integration branch upstream

    branchOrig = ed.getBranchesForRole(repo,roleBranches,"release")
    branchTgt = ed.getBranchesForRole(repo,roleBranches,"integration")
    fitness = ed.fracFitIntegration(repo, branchOrig, branchTgt, True) * weight

    return fitness

def rule_3_f_i_A(repo, weight, roleBranches, parameters):
    # Rule 3.f.i.A - Fix branches integrated into main branch upstream

    branchOrig = ed.getBranchesForRole(repo,roleBranches,"fix")
    branchTgt = ed.getBranchesForRole(repo,roleBranches,"main")
    fitness = ed.fracFitIntegration(repo, branchOrig, branchTgt, True) * weight

    return fitness

def rule_3_f_ii_A(repo, weight, roleBranches, parameters):
    # Rule 3.f.ii.A - Fix branches integrated into integration branch upstream

    branchOrig = ed.getBranchesForRole(repo,roleBranches,"fix")
    branchTgt = ed.getBranchesForRole(repo,roleBranches,"integration")
    fitness = ed.fracFitIntegration(repo, branchOrig, branchTgt, True) * weight

    return fitness

def rule_3_f_iii_A(repo, weight, roleBranches, parameters):
    # Rule 3.f.iii.A - Fix branches integrated into change branch upstream

    branchOrig = ed.getBranchesForRole(repo,roleBranches,"fix")
    branchTgt = ed.getBranchesForRole(repo,roleBranches,"change")
    fitness = ed.fracFitIntegration(repo, branchOrig, branchTgt, True) * weight

    return fitness

def rule_3_i_iii_C(repo, weight, roleBranches, parameters):
    # Rule 3.i.iii.C - Pull request before integration from Change branches

    branch = ed.getBranchesForRole(repo,roleBranches,"change")
    fitness = ed.fracFitPullRequests(repo, branch) * weight
    
    return fitness

def rule_3_i_v_C(repo, weight, roleBranches, parameters):
    # Rule 3.i.v.C - Pull request before integration from Fix branches

    branch = ed.getBranchesForRole(repo,roleBranches,"fix")
    fitness = ed.fracFitPullRequests(repo, branch) * weight
    
    return fitness

# Category 4
def rule_4_b_ii_B(repo, weight, roleBranches, parameters):
    # Rule 4.b.ii.B - Integration naming convention: develop

    branch = ed.getBranchesForRole(repo,roleBranches,"integration")
    fitness = ed.branchNamingFraction(repo, branch, ["develop"]) * weight

    return fitness

def rule_4_b_iv_A(repo, weight, roleBranches, parameters):
    # Rule 4.b.iv.A - Release branches following semantic versioning

    branch = ed.getBranchesForRole(repo,roleBranches,"release")
    #fitness = ed.fracFitSemVer(repo, branch, ["/release-"]) * weight
    fitness = ed.fracFitSemVer(repo, branch) * weight

    return fitness

def rule_4_b_iv_B(repo, weight, roleBranches, parameters):
    # Rule 4.b.iv.B - Release naming convention: release-*
 
    branch = ed.getBranchesForRole(repo,roleBranches,"release")
    fitness = ed.branchNamingFraction(repo, branch, ["release"]) * weight

    return fitness

def rule_4_b_v_A(repo, weight, roleBranches, parameters):
    # Rule 4.b.v.A - Fix branches following semantic versioning

    branch = ed.getBranchesForRole(repo,roleBranches,"fix")
    #fitness = ed.fracFitSemVer(repo, branch, ["/hotfix-", "/bugfix-", "/fix-"]) * weight
    fitness = ed.fracFitSemVer(repo, branch) * weight
    
    return fitness

def rule_4_b_v_B(repo, weight, roleBranches, parameters):
    # Rule 4.b.v.B - Fix branch naming convention: hotfix-*
    
    branch = ed.getBranchesForRole(repo,roleBranches,"fix")
    fitness = ed.branchNamingFraction(repo, branch, ["hotfix","bugfix","fix"]) * weight

    return fitness

def rule_4_c_i(repo, weight, roleBranches, parameters):
    # Rule 4.c.i - Tags used in Main branch

    branch = ed.getBranchesForRole(repo,roleBranches,"main")
    branchTags = ed.countTags(repo, branch)
    totalTags = ed.countTags(repo, "")
    fitness = 0
    
    if totalTags > 0:
        fitness = branchTags/totalTags * weight
    else:
        fitness = 0

    return fitness

def rule_4_c_iv(repo, weight, roleBranches, parameters):
    # Rule 4.c.iv - Tags used in Release branch

    branch = ed.getBranchesForRole(repo,roleBranches,"release")
    branchTags = ed.countTags(repo, branch)
    #totalTags = ed.countTags(repo, "")
    fitness = 0
    
    if branchTags > 0:
        fitness = 1.0 * weight
    else:
        fitness = 0.0

    return fitness

def rule_4_d(repo, weight, roleBranches, parameters):
    # Rule 4.d - Master branch assuming Main role

    totalTags = ed.countTags(repo, "")
    bumpVersions = ed.countBumpVersions(repo)
    fitness = 0

    if totalTags > 0:
        fitness = bumpVersions/totalTags * weight
    else:
        fitness = 0

    return fitness