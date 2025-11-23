# Migration Plan: mymcp → iproject

## Content Analysis

### KEEP in mymcp (Examples for Users)

#### results/
- ✅ `review_template.md` - Referenced in README.md, usecases/
- ✅ `review_965215.md` - Referenced in usecases/review_automation (example assessment)
- ✅ `README.md` - Documentation

#### analysis/
- ✅ `analysis_new_feature_966349/` - Complete example (referenced in usecases/)
- ✅ `analysis_new_feature_osprh_12802/` - In-progress example
- ✅ `HOW_TO_ASK.md` - Main documentation
- ✅ `README.md` - Documentation

### MOVE to iproject (Actual Work)

#### results/
- 📦 `review_5192.md` - GitHub PR assessment (actual work)
- 📦 `review_965216.md` - OpenDev review (actual work)
- 📦 `review_965239.md` - OpenDev review (actual work)
- 📦 `review_967773.md` - OpenDev review dashboard (actual work)
- 📦 `review_967773_patchset_1.md` - Patchset assessment (actual work)
- 📦 `review_pr_5232.md` - GitHub PR assessment (actual work)
- 📦 `TODO.md` - Work tracking (could keep or move)

#### analysis/
- 📦 `analysis_new_feature_966349_wip/` - WIP for 966349 (actual work)
- 📦 `analysis_new_feature_osprh_12802_wip/` - WIP for 12802 (actual work)
- 📦 `analysis_new_feature_osprh_15422/` - Spike (actual work)
- 📦 `analysis_new_feature_osprh_16421/` - Spike (actual work)
- 📦 `analysis_new_feature_osprh_16422/` - Spike (actual work)
- 📦 `analysis_new_feature_osprh_16423/` - Spike (actual work)
- 📦 `analysis_new_feature_osprh_16424/` - Spike (actual work)
- 📦 `analysis_new_feature_osprh_16426/` - Spike (actual work)
- 📦 `analysis_new_feature_osprh_16429/` - Spike (actual work)
- 📦 `analysis_new_feature_osprh_16644/` - Spike (actual work)
- 📦 `analysis/docs/` - Various old analysis documents (actual work)
- 📦 `analysis_review_966349_patchset_1.org.backup` - Old backup (actual work)
- 📦 `debug_keystone_*.sh` - Debug scripts (actual work)
- 📦 `HOWTO_WSGIDaemonProcess_apache_group_apache_processes_10_threads_2.org.backup` - Old backup (actual work)

## Migration Commands

```bash
cd <mymcp-repo-path>

# Move results
mv results/review_5192.md workspace/iproject/results/
mv results/review_965216.md workspace/iproject/results/
mv results/review_965239.md workspace/iproject/results/
mv results/review_967773.md workspace/iproject/results/
mv results/review_967773_patchset_1.md workspace/iproject/results/
mv results/review_pr_5232.md workspace/iproject/results/
mv results/TODO.md workspace/iproject/results/

# Move analysis work-in-progress directories
mv analysis/analysis_new_feature_966349_wip/ workspace/iproject/analysis/
mv analysis/analysis_new_feature_osprh_12802_wip/ workspace/iproject/analysis/

# Move spike directories
mv analysis/analysis_new_feature_osprh_15422/ workspace/iproject/analysis/
mv analysis/analysis_new_feature_osprh_16421/ workspace/iproject/analysis/
mv analysis/analysis_new_feature_osprh_16422/ workspace/iproject/analysis/
mv analysis/analysis_new_feature_osprh_16423/ workspace/iproject/analysis/
mv analysis/analysis_new_feature_osprh_16424/ workspace/iproject/analysis/
mv analysis/analysis_new_feature_osprh_16426/ workspace/iproject/analysis/
mv analysis/analysis_new_feature_osprh_16429/ workspace/iproject/analysis/
mv analysis/analysis_new_feature_osprh_16644/ workspace/iproject/analysis/

# Move old docs and backups
mv analysis/docs/ workspace/iproject/analysis/
mv analysis/*.backup workspace/iproject/analysis/
mv analysis/debug_keystone_*.sh workspace/iproject/analysis/

# Commit to iproject
cd workspace/iproject
git add results/ analysis/
git commit -m "Migrate actual work from mymcp

Moved all actual work artifacts (reviews, spikes, WIP docs) from mymcp
to iproject to keep mymcp clean and focused on tools + examples.

Content migrated:
- 7 review assessments
- 10 spike/feature analysis directories
- 2 WIP directories
- analysis/docs/ (old analysis documents)
- Debug scripts and backups
"
git push
```

## After Migration

mymcp will contain:
- Tools (scripts, MCP agents)
- Documentation (README, HOW_TO_ASK, IPROJECT guide)
- **2 example assessments** (review_965215.md, review_template.md)
- **2 example feature analyses** (966349, osprh_12802)

iproject will contain:
- All your actual review assessments
- All your actual feature analysis/spikes
- All WIP documents
- Historical analysis docs

## Verification

```bash
# Check what remains in mymcp
cd <mymcp-repo-path>
ls -la results/
ls -la analysis/

# Should see:
# results/:
#   - review_template.md
#   - review_965215.md
#   - README.md
#
# analysis/:
#   - analysis_new_feature_966349/
#   - analysis_new_feature_osprh_12802/
#   - HOW_TO_ASK.md
#   - README.md

# Check what's in iproject
cd workspace/iproject
ls -la results/
ls -la analysis/

# Should see all your actual work
```

