# 章节级索引（大文档）

来源: Confluence 在线拉取
阈值: >= 10KB | 文档数: 52

用法: 通过 Grep 搜索标题关键词 → 获取文件名 → 查 kb-confluence-map.json 获取 page_id → 在线读取

## `02-begin-with-deepctr.ipynb.md` (56KB, 1295行, 13节)

- L31: # configure
- L58: # write your dataset reader
- L125: ## test your dataset reader
- L669: ## create embedding fetch layer
- L717: ### test fetch feature embedding
- L730: # inlut is the data read from dataset, and its ps_context resources
- L744: # because the ps optimizer initiliazed as 0, so that the embs is all 0
- L965: ## create sub model, which can be exported by oneself used by predictor
- L1214: ## wrap the sub model into full model
- L1216: ### let constuct the input feed into sub model
- L1225: # get the pooled embedding from sparse_emb_layer
- L1233: ### let construct the full model
- L1243: # train the model

## `1_6_0 GPU pooling _ dense allreduce与worker pooling性能对比测试.md` (26KB, 172行, 19节)

- L1: # 相关背景
- L3: ## 实验环境
- L9: ## GPU机器和CPU机器的训练速度置换比计算方法
- L17: # 实验结果
- L19: ## cart_feat_unify_v4_hinet_v2_emb_new22_t_1_BR (batch_size=128)
- L45: ### CPU和GPU训练速度置换比
- L47: ## dd_din_lt_esmm_mpi_softsim_2k_cl_adf_mgdcn_v2_BR (batch_size=512)
- L69: ### CPU和GPU训练速度置换比
- L71: ## dsrm4_v5_ctr_prun_nn_t_5_l5 (batch_size=512)
- L93: ### CPU和GPU训练速度置换比
- L96: ## dsrm_v5_1_release
- L108: ### CPU和GPU训练速度置换比
- L110: ## pdp_vtt_unify_v3_TW
- L122: ### CPU和GPU训练速度置换比
- L124: ## pdp_multilabel_vc_search_cate_db_ship_1128_ID
- L136: ### CPU和GPU训练速度置换比
- L138: ## deepctr（测试用demo模型）
- L150: ### CPU和GPU训练速度置换比
- L153: # 结论

## `20220117_egotf v0_4.md` (10KB, 21行, 3节)

- L8: ### Day Auc
- L17: ### number of feature key in sparse table
- L20: ### time cost of training

## `20220127_egotf v0_4_1.md` (16KB, 17行, 3节)

- L5: ### Day Auc
- L14: ### number of feature key in sparse table
- L16: ### time cost of training

## `20220214_egotf v0_4_2.md` (27KB, 18行, 3节)

- L6: ### Day Auc
- L15: ### number of feature key in sparse table
- L17: ### time cost of training

## `20220316_egotf v0_4_3.md` (13KB, 14行, 3节)

- L1: # Experiment result for dd baseline model (dd_fgv7_session_pruning)
- L8: # Experiment result for assign-slots model
- L11: # Experiment result for pdp baseline model (sparsednn_pdpv2_multitask_tf_new)

## `20220606_egotf v0_4_5.md` (12KB, 13行, 4节)

- L1: # Experimental config: 32 workers with 10 cores, 100G memory for each worker.
- L3: # Experiment result for pdp baseline model (sparsednn_pdpv2_multitask_tf_nl9)
- L10: ### number of feature key in sparse table
- L12: ### time cost of training

## `20220709-egotf 0_4_6 _not with zmap optimisation and nsc development_.md` (28KB, 41行, 5节)

- L1: # Training from scratch performs the same
- L3: ## 1) Training Model: dd_feav4_po_fgv2_slotdropout_BR
- L16: ## 2) Training Model: sparsednn_pdpv4_adf_fpv2_d6_SG
- L25: # Incremental Training performs the same with directly training multi-days.
- L27: ## Training Model: dd_feav4_po_fgv2_slotdropout_BR

## `20220714_egotf v0_4_6.md` (24KB, 20行, 3节)

- L1: # Training from scatch performs the same
- L3: ## 1) Training Model: dd_feav4_po_fgv2_slotdropout_BR
- L12: ## 2) Training Model: sparsednn_pdpv4_adf_fpv2_d6_SG

## `About Inferencing (Release models to EGO predictor).md` (21KB, 328行, 22节)

- L3: # Workflow[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/Release%20models%20to%20ego%20predictor#workflow)
- L9: # Prepare config files[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/Release%20models%20to%20ego%20predictor#prepare-config-files)
- L33: # Release your model as a online serving[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/Release%20models%20to%20ego%20predictor#release-offline-training-model)
- L96: ### A. Release one checkpoint online
- L122: ### B. Release period checkpoint
- L137: ### C. Release mix checkpoint serving
- L151: ### D. Release a online learning serving
- L191: # View and operate batch model serving
- L193: ## View batch model serving list
- L195: #### UI
- L204: #### Shell: get_online_model_list.sh[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/View%20and%20operate%20online%20model#shell-get_online_model_listsh)
- L224: ## View Online Model Detail[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/View%20and%20operate%20online%20model#view-online-model-detail)
- L226: #### UI[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/View%20and%20operate%20online%20model#ui-1)
- L234: #### Shell: get_online_job_list.sh[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/View%20and%20operate%20online%20model#shell-get_online_job_listsh)
- L253: ## Config Grey Release
- L268: # View and operate online learning serving
- L270: ## View online learning serving list
- L276: ## Operate online learning serving
- L282: # How to take a PressTest
- L286: #### Step 1: Create a PressTest job
- L310: #### Step2: View a PressTest job
- L326: # How to Deploy a GR model

## `About Management.md` (11KB, 137行, 20节)

- L1: # 1.Project Management
- L5: ## 1.1 Resource Dashboard
- L16: ### 1.1.1 Resource information
- L25: ### 1.1.2 Real time status
- L29: ### 1.1.3 Running job usage
- L33: ### 1.1.4 History job usage
- L37: ## 1.2 Project Setting
- L39: ### 1.2.1 User management
- L49: ### 1.2.2 Resource management
- L60: ### 1.2.3 Project operation Record
- L64: ### 1.2.4 Job count limit setting
- L68: ### 1.2.5 Alert setting
- L72: ### 1.2.6 Checkpoint whitelist
- L77: # 2. CKPT Management
- L85: # 3. PS Management
- L105: # 4. Cost Management
- L109: ## 4.1 Cost Statement
- L117: ## 4.2 Summary Bill
- L129: ## 4.3 Cost Analysis
- L133: # 5. Notification Management

## `About Training Job.md` (30KB, 382行, 35节)

- L1: # Offline Training Job
- L14: ## Prepare Config Files[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#prepare-config-files)
- L41: ## Submit Batch Training Job[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#submit-batch-training-job)
- L43: #### UI[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#ui)
- L90: #### Shell: launch_job.sh[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#shell-launch_jobsh)
- L121: ## View Offline Training Job List[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#view-and-operate-offline-training-job)[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#view-training-job-list)
- L123: #### UI[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#ui-1)
- L138: #### Shell: get_job_list.sh[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#shell-get_job_listsh)
- L158: ## View Training Job Detail[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#view-training-job-detail)
- L160: #### UI[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#ui-2)
- L180: #### **Shell: get_job_status.sh**[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#shell-get_job_statussh)
- L198: ## Stop Training Job[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#stop-training-job)
- L200: #### UI
- L202: #### Shell: stop_job.sh[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#shell-stop_jobsh)
- L219: ## Delete Training Job[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#delete-training-job)
- L221: #### UI
- L225: #### Shell: delete_job.sh[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#shell-delete_jobsh)
- L242: ## Copy Training job
- L246: # Online Learning Job
- L248: ## Online learning job introduction[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Online%20Learning%20Job#online-learning-job-introduction)
- L252: ## Submit Online Learning Job[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Online%20Learning%20Job#submit-online-learning-job)
- L254: #### UI[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Online%20Learning%20Job#ui)
- L260: ## View Training Job List[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Online%20Learning%20Job#view-training-job-list)
- L266: ## View Online Learning Job Detail[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Online%20Learning%20Job#view-online-learning--job-detail)
- L272: ## Stop Online Learning Job[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Online%20Learning%20Job#stop-online-learning-job)
- L276: ## Delete and Copy Training Job[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Online%20Learning%20Job#delete-training--job)
- L280: # Period Training Job
- L282: ## Period training job introduction[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Period%20Training%20Job#period-training-job-introduction)
- L310: ## Submit Period Training Job[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Period%20Training%20Job#ui)
- L342: ## View Training Job List
- L346: ## View Period Training Job Detail
- L354: ## Verify & Start Period Training Job[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Period%20Training%20Job#verify--start-period-training-job)
- L362: ## Stop Period Training Job[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Period%20Training%20Job#stop-period-training-job)
- L366: ## Delete Period Training Job[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Period%20Training%20Job#delete-period-training--job)
- L372: # FAQ

## `Benchmark CPU vs GPU_主要是精排模型_.md` (14KB, 393行, 28节)

- L1: # Concept
- L11: # Deepctr Model
- L18: ## Result
- L24: ## 1. PredictV3
- L26: ### 1.1 911 items
- L34: ### 1.2 500 items
- L41: ## 2. Predict + fs+ fgv1
- L43: ### 2.1 911 items
- L49: ### 2.1 500 items
- L55: # Din Model
- L57: ## CPU C2_V2
- L73: ## GPU T4
- L86: ### GPU Optimize version
- L92: ### GPU Optimize version2
- L102: ## A30
- L110: # Din+sesion Model
- L122: # Search  model perf on G18_v3(A30) and C3V3(132c)
- L126: #### CPU
- L147: #### GPU
- L207: #### Conclusion
- L211: #### T4 VS A30
- L263: # G18V3 VS C3V3 from rcmd model
- L349: #### conclusion
- L353: # G18V3 VS C3V2 from mpi model
- L365: #### conclusion
- L369: # G18V3 VS S1V2 from video model
- L377: #### conclusion
- L385: # G18V3置换比例

## `EGO Core Metrics.md` (27KB, 157行, 24节)

- L1: # Performance
- L3: ## Training
- L5: ### CPU
- L7: #### Benchmark Plan
- L45: #### Metrics
- L47: ### GPU
- L49: #### Benchmark Plan
- L58: #### Metrics
- L60: ### 1.5.0 GPU测试
- L66: #### 实验结果
- L96: ## Inference
- L102: ### CPU
- L104: #### Benchmark Plan
- L106: #### Metrics
- L108: ### GPU
- L110: #### Metrics
- L112: ### GPU
- L114: # 成本
- L116: ## 训练成本 （ /job）
- L118: ## 推理成本 （ /request）
- L120: ## 资源使用率（训练+推理）
- L123: # 实效性
- L129: # 稳定性（SLI）
- L145: # 模型数

## `EGO Portal User Manual.md` (66KB, 933行, 89节)

- L1: # About Model and Version
- L7: ## Register Model
- L15: #### UI
- L21: #### Shell: create_model.sh
- L42: ## Register Model Version[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20model%20&%20version#register-model-version)
- L52: #### UI[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20model%20&%20version#ui-1)
- L64: #### Shell: create_model_version.sh[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20model%20&%20version#shell-create_model_versionsh)
- L88: ## View Model List[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20model%20&%20version#view-model-list)
- L90: #### UI[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20model%20&%20version#ui-2)
- L98: #### Shell: get_model_list.sh[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20model%20&%20version#shell-get_model_listsh)
- L116: ## Delete Model
- L118: #### UI[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20model%20&%20version#ui-3)
- L121: #### Shell: delete_model.sh[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20model%20&%20version#shell-delete_modelsh)
- L138: ## View Model Version List[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20model%20&%20version#view-model-version-list)
- L140: #### UI[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20model%20&%20version#ui-4)
- L147: #### Shell: get_model_version_list.sh[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20model%20&%20version#shell-get_model_version_listsh)
- L166: ## Delete Model Version[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20model%20&%20version#delete-model-version)
- L168: #### UI[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20model%20&%20version#ui-5)
- L171: #### Shell: delete_model_version.sh[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20model%20&%20version#shell-delete_model_versionsh)
- L189: ## View Checkpoint List[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20model%20&%20version#view-checkpoint-list)
- L191: #### UI[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20model%20&%20version#ui-6)
- L197: #### Shell: get_checkpoint_list.sh[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20model%20&%20version#shell-get_checkpoint_listsh)
- L218: ## Model& Version permission[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20model%20&%20version#model-version-permission)
- L223: # About Training Job
- L225: ## Offline Training Job
- L238: ### Prepare Config Files[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#prepare-config-files)
- L265: ### Submit Batch Training Job[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#submit-batch-training-job)
- L267: #### UI[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#ui)
- L295: #### Shell: launch_job.sh[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#shell-launch_jobsh)
- L326: ### View Offline Training Job List[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#view-and-operate-offline-training-job)[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#view-training-job-list)
- L328: #### UI[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#ui-1)
- L343: #### Shell: get_job_list.sh[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#shell-get_job_listsh)
- L363: ### View Training Job Detail[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#view-training-job-detail)
- L365: #### UI[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#ui-2)
- L385: #### **Shell: get_job_status.sh**[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#shell-get_job_statussh)
- L403: ### Stop Training Job[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#stop-training-job)
- L405: #### UI
- L407: #### Shell: stop_job.sh[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#shell-stop_jobsh)
- L424: ### Delete Training Job[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#delete-training-job)
- L426: #### UI
- L430: #### Shell: delete_job.sh[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Offline%20Training%20Job#shell-delete_jobsh)
- L447: ### Copy Training job
- L451: ## Online Learning Job
- L453: ### Online learning job introduction[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Online%20Learning%20Job#online-learning-job-introduction)
- L457: ### Submit Online Learning Job[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Online%20Learning%20Job#submit-online-learning-job)
- L459: #### UI[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Online%20Learning%20Job#ui)
- L465: ### View Training Job List[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Online%20Learning%20Job#view-training-job-list)
- L471: ### View Online Learning Job Detail[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Online%20Learning%20Job#view-online-learning--job-detail)
- L477: ### Stop Online Learning Job[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Online%20Learning%20Job#stop-online-learning-job)
- L481: ### Delete and Copy Training Job[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Online%20Learning%20Job#delete-training--job)
- L485: ## Period Training Job
- L487: ### Period training job introduction[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Period%20Training%20Job#period-training-job-introduction)
- L515: ### Submit Period Training Job[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Period%20Training%20Job#ui)
- L547: ### View Training Job List
- L551: ### View Period Training Job Detail
- L559: ### Verify & Start Period Training Job[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Period%20Training%20Job#verify--start-period-training-job)
- L567: ### Stop Period Training Job[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Period%20Training%20Job#stop-period-training-job)
- L571: ### Delete Period Training Job[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/About%20Training%20Job/Period%20Training%20Job#delete-period-training--job)
- L577: # About inferencing
- L579: ## Release models to EGO predictor
- L583: ### Workflow[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/Release%20models%20to%20ego%20predictor#workflow)
- L589: ### Prepare config files[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/Release%20models%20to%20ego%20predictor#prepare-config-files)
- L613: ### Release your model as a online serving[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/Release%20models%20to%20ego%20predictor#release-offline-training-model)
- L615: #### UI
- L675: ##### A. Release one checkpoint online
- L701: ##### B. Release period checkpoint
- L716: ##### C. release mix checkpoint serving
- L730: ##### D. Release a online learning serving
- L745: #### Shell: push_model_to_online_ps.sh[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/Release%20models%20to%20ego%20predictor#shell-push_model_to_online_pssh)
- L770: ## View and operate batch model serving
- L772: ### View batch model serving list
- L774: #### UI
- L784: #### Shell: get_online_model_list.sh[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/View%20and%20operate%20online%20model#shell-get_online_model_listsh)
- L804: ### View Online Model Detail[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/View%20and%20operate%20online%20model#view-online-model-detail)
- L806: #### UI[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/View%20and%20operate%20online%20model#ui-1)
- L814: #### Shell: get_online_job_list.sh[​](https://doc.mlp.shopee.io/EGO/EgoController/User%20manual/View%20and%20operate%20online%20model#shell-get_online_job_listsh)
- L833: ### Config Grey Release
- L848: ## View and operate online learning serving
- L850: ### View online learning serving list
- L856: ### Operate online learning serving
- L862: ## How to take a PressTest
- L866: #### Step 1: Create a PressTest job
- L890: #### Step2: View a PressTest job
- L904: # Project Management
- L908: ## 1.Resource Information
- L918: ## 2. User management and resource management
- L922: ## 3. Job count limit setting
- L926: ## 4. Alert setting
- L930: ## 5. Checkpoint archived setting

## `EGO Portal V0.4.0 PRD.md` (16KB, 331行, 16节)

- L1: ## 1.5 Changes
- L9: # 2 Requirements List
- L11: ## 2.1 Products involved
- L17: ## 2.2 Progress
- L77: # 3 Requirements in Detail
- L79: ## 3.1 Resource Dashboard
- L81: ### 3.1.1. Page Frame
- L95: ### 3.1.2 Resource Dashboard
- L119: ## 3.2 Notebook
- L160: ### 3.2.1 model - model management
- L186: ### 3.2.2 model - notebook
- L194: ## 3.3 Online Learning
- L251: ## 3.4 Train job
- L275: ## 3.5 Serving
- L314: ## 3.6 GNN
- L320: ## 3.7 Others

## `EGO Portal V0.5.0 PRD.md` (14KB, 242行, 11节)

- L1: ## 1.5 Changes
- L15: # 2 Requirements List
- L17: ## 2.1 Products involved
- L26: ## 2.2 Progress
- L134: # 3 Requirements in Detail
- L136: ## 3.1 PS management
- L144: ### 3.1.1 Frame Design
- L154: ### 3.1.2 PS Dashboard
- L172: ## 3.2 Cost management
- L182: ## 3.3 Notification management (Moved to 0.4.2)
- L224: ## 3.4 PressTest

## `EGO Portal V0.6.0 PRD.md` (13KB, 198行, 28节)

- L3: # 1. Overview
- L5: ## 1.1 Objectives and Significance
- L15: ## 1.2 Expected ROI
- L19: ## 1.3 Expected Release Time
- L23: ## 1.4 Prototype Link
- L27: ## 1.5 Changes
- L29: # 2 Requirements List
- L33: # 3 Requirements in Detail
- L35: ## 3.1 支持8bits量化
- L66: ## 3.2 支持predictor2.0及相关优化
- L97: ## 3.3 支持下载compile文件
- L103: ## 3.4 支持模型脉络
- L109: ### 1.需求目的
- L115: ### 2.需求概括
- L120: ### 3.依赖项
- L127: ### 4.需求设计
- L130: ## 3.5 eval任务正常计算资源
- L134: ## 3.6 优化训练任务的配置，推广智能资源推荐和扩缩
- L144: ### 3.6.1 支持展示所设资源的总和
- L152: ### 3.6.2 支持跳过sandbox
- L156: ### 3.6.3优化时间配置的样式
- L164: ### 3.6.4选择model时支持过滤区分是否是自己的
- L168: ### 3.6.5 修改优先级上下限
- L180: ### 3.6.6支持load ckpt/导入外部参数二选一
- L184: ### 3.6.7 增加job 日志
- L186: ## 3.7 fix压测相关的功能
- L192: ## 3.8 serving 文件配置优化
- L196: ## 3.9进一步支持git上传

## `EGO Portal V0.7.5 PRD.md` (15KB, 87行, 4节)

- L1: ### 1. ol&period train 融合
- L47: ### 2.多塔模型版本一致性检验
- L64: ### 3.支持“graph only 模式"压测
- L76: ### 4.支持灰度功能

## `EGO Portal V0.8.2 PRD-智能机器人项目调研与demo设计.md` (15KB, 57行, 18节)

- L1: ## 第一部分：背景与场景
- L3: ### 一、背景和目标
- L5: ### 二、使用场景举例
- L8: ## 第二部分：流程与Demo说明（初步设想）
- L15: ## 第三部分：竞品调研及方案汇总
- L17: ### 三、竞品功能调研
- L19: #### 3.1 （内部产品）-DI Diana
- L21: #### 3.2 （外部）腾讯云 智能对话机器人
- L24: #### **3.3 （外部）阿里云 Intelligent Advisor**
- L26: #### 3.4 **（外部）百度智能云-智能助手**
- L28: #### 3.5 （外部）Apple Support Assistant
- L31: ### 四、竞品参考价值打分
- L33: ### 五、智能问答机器人功能的细项能力梳理和对比
- L35: ### 六、公司内部相关能力总结
- L37: #### 6.1 Compass Assistant
- L43: #### 6.2 Seatalk AI Bot Platform
- L49: #### 6.3 smart
- L55: #### 6.4. Alpha 知识库

## `EGO Portal V0.9.0 PRD.md` (19KB, 185行, 21节)

- L1: ## 1.5 Changes
- L11: # 2 Requirements List
- L14: ## 1. 增设EGO个人概览页面
- L32: ###### _1.背景_
- L38: ###### _2. 预期收益_
- L44: ###### _3. 页面概念澄清_
- L50: ## 2.支持huatuo项目
- L72: ## 3.支持服务组
- L78: ## 4. 支持VQ
- L88: ## 5. 支持周期性训练可自定义跳过大促数据
- L92: ## 6. serving：流量情况显示到详情页&增加ckpt时间列
- L100: ## 7. 周期性训练失败后支持一键retry重试
- L102: ## 8. 优化下线模型机制和已下线模型的流量显示
- L118: ## 9. 支持在线修改文件
- L126: ## 10. customize 类型的周期性训练支持对ckpt进行处理
- L128: ## 11. 周期性训练列表页增加一列显示最新的job的状态
- L132: ## 12.周期性训练支持自定义dump的频率
- L136: ## 13.ckpt 垃圾桶支持按照name/id搜索
- L140: ## 14. 支持多种情况的ckpt互传
- L148: ## 15. 资源管理页面v2
- L162: ## 16. 服务下线逻辑优化

## `EGO Team Introduction.md` (15KB, 78行, 33节)

- L3: ## **arthur.hu**
- L7: ## **baolong.guo\*\***(Resigned)\*\*
- L10: ## **bill.wu**
- L14: ## **dang.truong**
- L16: ## **feichao.ma**
- L18: ## **fulong.tan\*\***(Resigned)\*\*
- L20: ## **huaidong.gao**
- L22: ## **jian.yang**
- L24: ## **jinghao.feng\*\***(Transferred)\*\*
- L26: ## **jingzhe.zhou**
- L28: ## **joyce.teo**
- L30: ## **junchen.li**
- L32: ## **liufang\*\***(Resigned)\*\*
- L35: ## \*\*mingze.wei
- L38: ## \*\*
- L41: ## **nick.yi**
- L43: ## **shanshan.jiang\*\***(Resigned)\*\*
- L45: ## **shibin.chen**
- L47: ## **shuquan.huang**
- L49: ## **sixiang.yang**
- L51: ## **szewen.seet**
- L53: ## **tiantian.duan**
- L55: ## **xiang.zhang**
- L57: ## **xuefeng.zhu(Resigned)**
- L59: ## **yadong.wang**
- L61: ## **yanbin.zhao**
- L63: ## **yansheng.zhang**
- L65: ## **zhijie.he**
- L67: ## **shaochen.sun**
- L70: ## **shaoning.zheng**
- L73: ## **peng.liulp**
- L76: ## **yifan.jiang**
- L78: ## Others(Resigned):

## `EGO V0_4 API Manual.md` (15KB, 243行, 33节)

- L15: ### Tile Pooling
- L23: ### Slot Category
- L37: #### txt format sample
- L41: #### protobuf format sample
- L45: ### Assign Slot
- L53: #### replace_gradient
- L57: ## FeatureDense
- L61: ### Usage
- L65: # Variable
- L69: ## Usage
- L79: # Layer & Module
- L85: ## ego.layers.Activation
- L89: ## ego.layers.Dense
- L95: ## ego.layers.Normalization
- L110: ## ego.modules.DenseTower
- L116: # Round
- L118: ## Label & LossWeight
- L124: ### txt format sample
- L132: ### protobuf format sample
- L138: ## Round(egotf 0.4.2 and previous)
- L157: ## [Target declaration (egotf 0.4.3 and above)](<https://confluence.shopee.io/pages/viewpage.action?pageId=1000816697&moved=true#Attention:updatesinmodeldefinition(egotf0.4.3andabove)-declareatarget>)
- L168: ## [OfflineRound and OnlineRound (egotf 0.4.3 and above)](<https://confluence.shopee.io/pages/viewpage.action?pageId=1000816697#Attention:updatesinmodeldefinition(egotf0.4.3andabove)-rounddefinition>)
- L179: # Compile
- L193: ## Compile separately for Training and Serving Graphs
- L201: ### Extra Validation Step (egotf 0.4.2 and previous)
- L209: # ADF
- L215: # Others
- L217: ## ego.add_print(items)
- L223: ## ego.add_print_vars_to_hdfs (egotf 0.4.2 and above)
- L227: ## ego.add_predict(target, target_name)
- L233: ## ego.add_print_vars_to_log (egotf 0.4.2 and above)
- L237: ## [How to use Tensorboard in (egotf 0.4.2 and above)](https://confluence.shopee.io/pages/viewpage.action?pageId=952768276&moved=true)
- L241: ## (egotf 0.4.6 and above)

## `EGOPortal V0.1.0 PRD.md` (14KB, 192行, 21节)

- L5: # 2 Requirements List
- L7: ## 2.1 Products involved
- L30: ## 2.2 User Flow
- L32: ## 2.3 Platform Architecture
- L50: # 3 Requirements in Detail
- L52: ## 3.1 Permission management
- L54: ### 3.1.1 Function Description
- L86: ### 3.1.2 Prototype screenshots
- L88: ## 3.2 Model management
- L90: ### 3.2.1 Function Description
- L126: ### 3.2.2 Field Description
- L132: ### 3.2.3 Prototype screenshots
- L142: ## 3.3 Offline Training
- L144: ### 3.3.1 Function Description
- L168: ### 3.3.2 Field Description
- L170: ### 3.3.3 Prototype screenshots
- L176: ## 3.4 Online Serving
- L178: ### 3.4.1 Function Description
- L187: ### 3.4.2 Prototype screenshots
- L189: # 4. Appendix
- L191: ## 4.1 Country enumeration values

## `EGOPortal V0.2.0 PRD.md` (11KB, 220行, 22节)

- L3: # 2 Requirements List
- L5: ## 2.1 Products involved
- L30: ## 2.2 User Flow
- L32: # 3 Requirements in Detail
- L34: ## 3.0 Original function modification
- L36: ### 3.0.1 Offline Training List & New Offline Training Job
- L52: ### 3.0.2 删掉new training job与release online model中的env
- L54: ## 3.1 Online Learning
- L56: ### 3.1.1 Online Learning Job List
- L71: ### 3.1.2 New Online Learning Job
- L79: ### 3.1.3 Online Learning Job Detail
- L99: ### 3.1.4 Online Learning Release
- L105: ## 3.2 Online Model Serving
- L107: ### 3.2.1 Online Model Serving List
- L115: ### 3.2.2 Update Online Model Serving
- L123: ### 3.2.3 Online Learning Serving Detail
- L125: ## 3.3 Period Training
- L127: ### 3.3.1 Period Training Rule List
- L156: ### 3.3.2 New Period Training Strategy
- L170: ### 3.3.3 Period Training List
- L181: ### 3.3.4 Update & Verify & Start Period Training Rules
- L200: ### 3.3.5 Period Training Release

## `EGOPortal V0.3.0 PRD.md` (16KB, 301行, 32节)

- L3: # 2 Requirements List
- L5: ## 2.1 Products involved
- L35: # 3 Requirements in Detail
- L37: ## 3.1 Batch Training Serving
- L39: ### 3.1.1 Batch Training Serving List
- L52: ### 3.1.2 New Batch Model Serving
- L54: #### 1.Overview
- L79: #### **2. Design**
- L82: ### 3.1.3 Update Batch Training Serving
- L98: ### 3.1.4 Batch  Model Basic Information
- L115: ### 3.1.5 Canary Release
- L117: #### **1.**Canary config
- L142: #### **2.rollback**
- L148: #### **3.Process**
- L176: ## 3.2 Online Learning Serving（第二期做）
- L178: ## 3.3 PressTest
- L184: ### 3.3.1 PressTest list
- L190: ### 3.3.2 New PressTest
- L228: ###  3.3.3 View info and result
- L242: ### 3.3.4 支持online learning发布时配置update threshold
- L257: ## 3.4 Training Job
- L259: ### 3.4.1 Online export Job (cancelled)
- L261: #### 1.online export job list
- L265: #### 2.New a online export job
- L267: #### 3.view online export job
- L277: ### 3.4.2 Job page new layout
- L279: #### 1.offline training job
- L285: #### 2 period training job
- L287: #### 3. online learning job
- L289: ### 3.4.3 支持配置greedy load mode开关从而增删优化器
- L295: ## 3.5 Management-Project management
- L297: ### 3.5.1 支持按照project查看release 和offline操作的操作记录

## `EGOPortal V0.3.1 PRD.md` (17KB, 426行, 29节)

- L1: ## 1.5 Changes
- L83: # 2 Requirements List
- L85: ## 2.1 Products involved
- L94: # 3 Requirements in Detail
- L96: ## 3.1 Batch Training Serving
- L98: ### 3.1.1 Batch Training Serving List
- L106: ### 3.1.2 New batch model serving
- L122: #### 3.1.2.1 New a Merge Models Serving
- L138: ### 3.1.3 Batch  Model Serving Basic Information
- L144: #### 3.1.3.1 **为新\*\***类型的batch model serving展示信息\*\*
- L152: #### **3.1.3.2 增加报警配置**
- L233: ### 3.1.4 Others：
- L239: ## 3.2 Online Learning Serving
- L241: ### 3.2.1 Online Learning Serving List
- L248: ### 3.2.2 New Online Learning Serving
- L265: ### 3.2.3 Update Online Learning Serving
- L271: ### 3.2.4 Online Learning Serving Basic Information
- L283: ## 3.3 Management
- L285: ### 3.3.1 Notification Management
- L320: ### 3.3.2 Project management
- L330: ### 3.3.3 CKPT Management
- L340: ### 3.3.4 Project management-dashboard
- L346: ## 3.4 Training &Model
- L348: ### 3.4.1 Support NSC(Negative Sample Center）
- L352: ### 3.4.2 Period training
- L382: ### 3.4.3 half precision and AUC alert
- L394: ### 3.4.4 支持load parameter时过滤nn
- L400: ### 3.4.5 model &ckpt list 优化
- L420: ### 3.4.6 优化点：调整三种train job的详情页部分字段的顺序

## `Ego Design Doc v0_1.md` (10KB, 167行, 8节)

- L1: # Purpose of this document
- L27: # Architecture of EGO 0.1
- L29: ## Concept Vocabulary
- L56: ## Architecture
- L92: # Key Features of EGO 0.1
- L144: ## Roadmap of EGO
- L151: # Examples
- L161: # Develop Plan

## `Ego FAQ.md` (12KB, 175行, 16节)

- L14: # Controller
- L18: ### **Q1. Why was my Checkpoint deleted & How to prevent a ckpt from being deleted?**
- L24: ### **Q2. Why am I unable to delete a version?**
- L31: ### Q3. Why can't I open the notebook?
- L39: ### Q4. how to print tensor in Notebook
- L47: ### **Q5. **How do I submit a GPU training job?
- L53: ### **Q6. Why is my job stuck in the ps prealloc_mem task**?
- L65: ### **Q7. When trying to submit a train job, an error message appears: offlineps not found**
- L71: ### **Q8. \*\***Questions about using periodic training\*\*
- L87: ### **Q9. How to prevent my serving from being offline**
- L91: ### **Q10. If the online model has not been updated for a long time, how can I configure the alarm?**
- L97: ### **Q11. What should I do if I can't turn on Ego's monitoring?**
- L101: ### **Q12. How do I apply for EGO permissions?**
- L113: ### **Q13. How to publish across Zones? For example, I want to train in sg and publish to us**
- L143: ### **Q14. How to set up relatively complex period rules?**
- L171: # Perf

## `Ego Full Configuration Preview.md` (10KB, 297行, 15节)

- L9: # Environment setting in egotf
- L33: # The batch size in training
- L41: # sparse feature elimination
- L45: # there are 3 ways to reduce the amount of sparse feature keys
- L47: # method 1: if the unseen day has exceeded the delete_after_unseen_days, right now, we train model hourly. so the days at here means hours. If the feature key is seen in current hour, its 'unseen_days' will be reset to 0, or unseen_day += 1
- L51: # method 2: if the score is below than delete_threshold
- L55: # Feature score = ((show - clk) _ nonclk_coeff + clk _ clk_coeff) / max(1, unseen_days)
- L61: # method 3: if the amount of feature keys exceeds the max_features, the superfluous feature keys with lower scores will be filtered out.
- L65: # Whether or not shuffle all samples between all workers.
- L231: # **deprecated**, mf_plugin controls the updated rules of mf_emb.
- L249: # **deprecated**, lr_plugin controls the updated rules of lr_emb. the dim of lr_emb is 1 fixed. emb = mf_emb + lr_emb
- L263: # cvm_plugin counts show time and click time of each feature key with a decay rate in one hour.
- L269: # adf_plugin accumulate "adf_vector" in each sample to capture the user's habits.
- L283: # if use tf backend, it must be configured.
- L295: # if not use tf backend, it must be configured.

## `Ego Predictor Guardian.md` (12KB, 259行, 20节)

- L1: # Master 服务
- L5: ## 数据结构:
- L29: ## 当用户部署新行时：
- L52: ## 当行属性发生变更时：
- L62: ## 当用户部署删除模型或者更新模型资源用量时：
- L74: ## 当模型版本更新时：
- L78: ## 当Predictor镜像/配置更新时：
- L84: ## Schedule的定期调度：
- L102: ## 路由：
- L110: # 模型路由算法
- L112: ## 背景
- L116: ## 设计目标
- L118: ### 功能目标
- L125: ### 非功能目标
- L132: ## 概念及抽象
- L140: ## 问题和困难
- L147: ## 调度算法
- L149: ### Input
- L167: ### Output
- L174: ### Algo

## `EgoBox_gpu pull优化_性能测试.md` (17KB, 117行, 18节)

- L1: ## 总结：
- L3: ### dsrm_v552
- L5: #### **测试背景**
- L10: #### **Round1 性能结果对比**
- L12: #### Round0 性能结果对比
- L14: #### **性能分析**
- L39: ### cvr_v21_delay_br
- L41: #### **测试背景**
- L46: #### **Round1 性能结果对比**
- L48: #### Round0 性能结果对比
- L50: #### **性能分析**
- L75: ### cart_unify
- L77: #### **测试背景**
- L82: #### **Round2 性能结果对比**
- L84: #### **Round1 性能结果对比**
- L86: #### Round0 性能结果对比
- L88: #### **性能分析**
- L115: ### 结论

## `EgoPredictor X Qir.md` (19KB, 363行, 4节)

- L1: ## Predictor-Proxy 技术文档
- L343: ## EgoPredictor在线服务的使用
- L349: ## 监控平台
- L357: ## 模型发布流程

## `EgoTrain Extensions.md` (11KB, 108行, 10节)

- L11: ### cel-plugin (draft version1)
- L30: ###  cei-plugin (draft2)
- L32: ###### **Running in Sample server**
- L38: ###### Running in Worker
- L43: ###### Running in Worker-coordinator
- L50: ## EgoPlugin (new)
- L61: ### ego-plugin.yaml
- L71: ### SampleServerPlugin
- L78: ### WorkerPlugin
- L98: ### CoordinatorPlugin

## `EgoTrainV1 IO module update.md` (12KB, 126行, 21节)

- L1: # 目标
- L6: # 问题
- L10: # 当前架构
- L22: # 优化点：
- L24: ## 减少batchfea到string之间的转换次数
- L30: ## Worker数据接收与存储模块优化
- L32: ### Worker中允许缓存多天的数据
- L39: ### 去除"RemoteIO BatchFea Queue"，BatchFea缓存功能下沉到RemoteIO中
- L44: ### Worker端固定使用磁盘缓存BatchFea，去掉pass size的限制
- L48: ### Worker请求SampleServer，采用最大堆策略 (如果采用磁盘缓存数据，是否还有需要？在天级任务中需要)
- L53: ## SampleServer数据解析模块优化
- L55: ### DailyIO解析样本并组装成BatchFea流程优化
- L57: #### 方案1：
- L61: ##### "Shuffle Ins Queue"的实现
- L68: #### 方案2：
- L75: # 待解决：
- L77: ## 在Colocate模式下，如何避免或减轻SampleServer和Worker进程之间互相抢占CPU造成性能下降。如何协调Worker和SampleServer进程。
- L79: ## 如何均匀的向各个worker分发数据。
- L81: ### 方案1：在colocate模式下，将Worker和SampleServer绑定，即这个worker固定向同pod内SampleServer请求数据。这样通过WorkerCoordinator均匀向SampleServer分发文件的功能，基本能保证Worker间数据是均匀的。同时，Shuffle能力并不减弱。
- L83: ## 能否将BatchFea变成一块连续内存，省掉序列化和反序列化。
- L85: # 具体优化方案：

## `Guardian User Manual.md` (13KB, 247行, 31节)

- L1: ## 1. **查看集群Debug信息，查看路由信息**
- L10: ## 2. **发布/卸载模型，更新/卸载subset，发布/删除集群**
- L29: ## 3. **自动扫描并发布S3模型**
- L39: # model_namespace需要对齐线上cluster name
- L40: # publish_at_least_valid_model_protect指的是至少扫到有这么多个模型 才会执行发布流程，是简单的保护机制 可以设置为1
- L41: # model_name_prefix 是过滤模型的prefix用的，我们发布到gpu集群的模型和cpu的模型都在一个project下 所以需要这种过滤
- L44: ## 4. **对非Guardian集群标记卸载模型**
- L61: ## 5. **测试路由正确性、测试模型在多个集群上的response信息是否一致**
- L70: # 修改代码中的opts.redis_key = "cty_cluster_divert_k8s_pdp_test";来改变路由到的集群
- L71: # @test_with_rpc_reply 仅让该进程测试路由可达性
- L72: # @port dummy port 可以看一些路由可达性的bvar指标
- L73: # 代码中包含了3个list:
- L74: # model_list:模型列表，可以包含所有你期望自动路由的或者不期望自动路由的模型列表
- L75: # non_dynamic_model:非动态路由模型列表
- L76: # dynamic_remote_list:动态路由集群ip列表
- L77: # 工具会随机访问model_list中的模型
- L78: # 如果是non_dynamic_model中的模型，但是最终流量打到了dynamic_remote_list中，会记录一次错误，并打印Warning日志
- L79: # 如果不是non_dynamic_model中的模型，但是最终流量没有打到dynamic_remote_list中，会记录一次错误，并打印Warning日志
- L80: # 如果response结果失败会记录一次错误，并打印Warning日志
- L86: # 启动进程后，使用rpcreplay 回放线上dump下的流量到这个实例 e.g. ./replay.sh --dir=/data/shuquan.huang/ego-predictor-guardian/build/run2/rpc2/ --timeout_ms=3000 --qps=1 --times=1000000 --server=0.0.0.0:1234
- L87: # 观察log情况
- L90: ## 6. **查看Guardian调度事件/监控**
- L94: ## 禁用Guardian调度相关功能
- L105: ## 7. **相关工具**
- L118: ## 8. **迁移Guardian指南**
- L120: #### a) 在lyra上创建集群
- L126: #### b) 在guardian上发布cluster meta信息
- L188: #### c) 发布模型
- L236: #### d) 确认模型可达
- L245: #### e) 卸载旧集群的模型
- L247: #### f) 将scanner例行，扫描S3目录，自动发布与卸载模型

## `Guidelines of using EGO Plugin V1.md` (23KB, 226行, 42节)

- L7: #### Step4: build up [libego-plugin-v1.so](http://libego-plugin-v1.so) and copy it to EGO_TASK_DIR
- L11: #### Step5: prepare a ego-plugin.yaml in the same dir with [libego-plugin-v1.so](http://libego-plugin-v1.so)
- L13: ## Add C++ "data converter" in data-reading pipeline
- L19: ### Apply built-in "data converter"
- L23: #### Step1: download a right version of libego-plugin-v1.so
- L27: #### Step2: prepare ego-plugin.yaml in the same dir with libego-plugin-v1.so
- L29: ##### SlotReassignConverter:
- L33: ##### SlotDuplicateConverter:
- L37: ##### DropSlotConverter:
- L41: ##### SlotReverseConverter:
- L45: ##### define multiple data converters
- L49: #### Step3: add ego_plugin_path in ego-learner.yaml
- L51: ### Tips about online serving
- L56: ### Implement a new user-defined "data converter" by yourself
- L60: #### Step1: clone the ego-plugin-v1 project.
- L64: #### Step2: enter the image
- L68: #### Step3: implement a new "data converter"
- L75: #### Step4: build up libego-plugin-v1.so and copy it to EGO_TASK_DIR
- L79: #### Step5: prepare a ego-plugin.yaml in the same dir with libego-plugin-v1.so
- L81: ## Adjust labels and weights, or drop out useless sparse feature keys in the training process
- L86: # What is ego-plugin-v1 project
- L90: ### Plugin functions in SampleServer
- L98: #### configurations in ego-plugin.yaml
- L107: #### InitSS function
- L113: #### ConvertSamplePackage function
- L118: #### FinalizeSS function
- L124: #### Implement your own "data converter"
- L128: ##### CustomizedDataConverter class
- L133: #### ParseMsgAndProcessOnSS
- L138: ### Plugin functions in Worker
- L143: #### configurations in ego-plugin.yaml
- L151: #### InitWorker
- L157: #### BeforeSessionRun
- L170: #### AfterSessionRun
- L185: #### FinalizeWorker
- L189: ### Plugin functions in WorkerCoordinator
- L193: #### configurations in ego-plugin.yaml
- L200: #### **InitWC**
- L206: #### ParseMsgsAndProcessOnWC
- L216: #### FinalizeWC
- L220: ### Example of EgoPlugin,** [clustering embedding learning algorithm](https://arxiv.org/abs/2302.01478)**
- L226: ### Plugin functions in Metric Calculation

## `How to use cpp converter.md` (38KB, 939行, 55节)

- L3: ### References
- L7: ### How to Debug Cpp Converters
- L11: ### How to Debug Cpp Converters
- L29: ## Images
- L33: ## Converts
- L37: ### LuaExtractor
- L55: ### LabelExtractor
- L89: ### MultitaskExtractor
- L113: ### DenseExtractor
- L129: ### DenseExtractorV2
- L153: ### SparseExtractor
- L165: ### StableCheck
- L175: ### FilterByTimestamp
- L189: ### FilterByDebugInfo
- L203: ### FilterByActionInfoAndDebugInfo
- L217: ### AdfDenseFeature
- L231: ### FilterBySampleId
- L245: ### ExtractUserIdFromSampleId
- L259: ### DenseExtractorFromDebuginfo
- L277: ### DenseExtractorFromSampleId
- L295: ### ExtractRequestIdFromSampleId
- L312: ### ExtractOriginFeatureFromDebugInfo
- L326: ### LabelMapping
- L340: ### ExtractInt64Feat
- L358: ### NegativeSample
- L394: ### GetSparseFeatureKeys
- L416: ### ConvertFeatureDenseToSparse
- L430: ### ShowClickExtractor
- L456: ### SlotMapping  (V1.8.2)
- L474: ### SlotMappingByScenario (V1.8.2)
- L500: ### FilterBySampleIdAndDebugInfo (V1.8.2)
- L514: ### FilterByActionInfoAndSampleIdAndDebugInfo (V1.8.2)
- L528: ### FilterBySome (V1.8.2)
- L556: ### ReplaceFeatureKey (V1.8.2)
- L568: ### ConstDenseFeature (V1.8.2)
- L582: ### MergeByRequestId (V1.8.2)
- L600: ### MergeByRequestIdCustom (V1.8.2)
- L639: ### DeduplicationCommonFeature (V1.8.2)
- L645: ### ExtensionInfo (V1.8.2)
- L667: ### DenseExtractorFromItemAttribute (V1.8.2)
- L685: ### DenseSlotMappping (V1.8.2)
- L703: ### DenseSlotMapppingByScenario(V1.8.2)
- L729: ### NegativeSampleNonContinuousUser  (V1.8.2)
- L751: ### ModSparseFeatures (V1.8.2)
- L765: ### SparseSlotFilterByScenario (V1.8.2)
- L783: ### CountOccurrencesInSequence (V1.8.2)
- L797: ### ColoringLabelInRequest (V1.8.2)
- L811: ### IfClickRequest (V1.8.2)
- L819: ### AggregationSampleId (V1.8.2)
- L825: ### CountActionInRequest (V1.8.2)
- L831: ### ReplaceSampleId (V1.8.3)
- L851: ### DuplicateSample (V1.8.3)
- L875: ### SparseReassign (V1.8.3)
- L897: ### SparseExtractorV2 (V1.8.3)
- L921: ### TagMergeDenseFeature (Not Published Yet)

## `L4 在线服务测试.md` (16KB, 202行, 13节)

- L1: # Summary
- L5: # gpucart：
- L13: # gpuddmy:
- L17: # gpuvideo:
- L23: # video2(cpu)
- L52: # video5(cpu)
- L107: # livestream:
- L111: # livestream2(cpu)
- L127: # search:
- L131: ## 线上实际迁移
- L184: ## pdp-ads
- L190: ## pdp-organic
- L198: ## search-gpusguide-dynamic

## `S1V2与C3机器置换比测试.md` (15KB, 78行, 23节)

- L3: ### 机型对比
- L5: ## Search:
- L7: ### dsrmV552 (search, rank)
- L9: #### C3: [https://ego-portal.mlp.live-test.shopee.io/training/job/1601118/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1601118/detail/info?tab=task), [https://ego-portal.mlp.live-test.shopee.io/training/job/1601258/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1601258/detail/info?tab=task), [https://ego-portal.mlp.live-test.shopee.io/training/job/1601410/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1601410/detail/info?tab=task), [https://ego-portal.mlp.live-test.shopee.io/training/job/1600231/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1601258/detail)
- L11: #### S1V2: [https://ego-portal.mlp.live-test.shopee.io/training/job/1601135/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1601135/detail/info?tab=task), [https://ego-portal.mlp.live-test.shopee.io/training/job/1601595/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1601595/detail/info?tab=task), [https://ego-portal.mlp.live-test.shopee.io/training/job/1601504/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1601504/detail/info?tab=task)
- L13: ##### 总结：C3:S1V2=1:3
- L21: ### prerank_v6_1_dcn_v2_unified_full (search, rough rank)
- L23: #### C3: [https://ego-portal.mlp.live-test.shopee.io/training/job/1615700/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1615700/detail/info?tab=task), [https://ego-portal.mlp.live-test.shopee.io/training/job/1615729/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1615729/detail/info?tab=task), [https://ego-portal.mlp.live-test.shopee.io/training/job/1616300/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1616300/detail/info?tab=task), [https://ego-portal.mlp.live-test.shopee.io/training/job/1616298/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1616298/detail/info?tab=task), [https://ego-portal.mlp.live-test.shopee.io/training/job/1614984/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1614984/detail/info?tab=task)
- L27: ##### 总结：C3:S1V2=1:4
- L34: ## Rcmd:
- L36: ### dd_dm_sdm_rt_v3_esmm_price_id_pow_ID (python converter, rcmd, recall)
- L38: #### C3: [https://ego-portal.mlp.live-test.shopee.io/training/job/1610257/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1610257/detail/info?tab=task), [https://ego-portal.mlp.live-test.shopee.io/training/job/1608574/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1608574/detail/info?tab=task), [https://ego-portal.mlp.live-test.shopee.io/training/job/1605584/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1605584/detail/info?tab=task)
- L40: #### S1V2: [https://ego-portal.mlp.live-test.shopee.io/training/job/1607950/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1607950/detail/info?tab=task)
- L42: ##### 总结：C3:S1V2=1:5
- L49: ### ranking-pdp-25-8-60-pre-optim (rcmd, rough rank)
- L51: #### C3: [https://ego-portal.mlp.live-test.shopee.io/training/job/1612709/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1612709/detail/info?tab=task), [https://ego-portal.mlp.live-test.shopee.io/training/job/1612385/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1612385/detail/info?tab=task), [https://ego-portal.mlp.live-test.shopee.io/training/job/1612542/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1612542/detail/info?tab=task)
- L53: #### S1V2: [https://ego-portal.mlp.live-test.shopee.io/training/job/1612714/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1612714/detail/info?tab=task), [https://ego-portal.mlp.live-test.shopee.io/training/job/1612384/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1612384/detail/info?tab=task), [https://ego-portal.mlp.live-test.shopee.io/training/job/1611036/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1611036/detail/info?tab=task), [https://ego-portal.mlp.live-test.shopee.io/training/job/1610889/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1610889/detail/info?tab=task)
- L55: ##### 总结：C3:S1V2=1:3
- L62: ### cross_scen_cvr_model3_v31_base2_ID (CR, rcmd, rank)
- L64: #### C3: [https://ego-portal.mlp.live-test.shopee.io/training/job/1614263/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1614263/detail/info?tab=task), [https://ego-portal.mlp.live-test.shopee.io/training/job/1614535/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1614535/detail/info?tab=task), [https://ego-portal.mlp.live-test.shopee.io/training/job/1614292/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1614292/detail/info?tab=task), [https://ego-portal.mlp.live-test.shopee.io/training/job/1613230/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1613230/detail/info?tab=task)
- L66: #### S1V2: [https://ego-portal.mlp.live-test.shopee.io/training/job/1614262/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1614262/detail/info?tab=task), [https://ego-portal.mlp.live-test.shopee.io/training/job/1614565/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1614565/detail/info?tab=task), [https://ego-portal.mlp.live-test.shopee.io/training/job/1614054/detail/info?tab=task](https://ego-portal.mlp.live-test.shopee.io/training/job/1614054/detail/info?tab=task)
- L68: ##### 总结：C3:S1V2=1:4
- L76: ### 总结：

## `SS优化_Search CTR_收益统计.md` (13KB, 111行, 52节)

- L3: ## 测算方式：
- L9: ## 周期性训练任务：
- L11: ### [https://ego-portal.mlp.shopee.io/training/periodRule/2436/detail/info?current=1&pageSize=10&tab=jobs](https://ego-portal.mlp.shopee.io/training/periodRule/2436/detail/info?current=1&pageSize=10&tab=jobs)(完成迁移)
- L13: #### 带SS优化的镜像：[https://ego-portal.mlp.shopee.io/training/job/29786959/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/29786959/detail/info?tab=task)
- L15: #### 带SS优化的镜像，调整read_threads: [https://ego-portal.mlp.shopee.io/training/job/30501309/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30501309/detail/info?tab=task)
- L17: #### 不带SS优化的镜像：[https://ego-portal.mlp.shopee.io/training/job/29746599/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/29746599/detail/info?tab=task)
- L19: #### 资源收益：缩减17个SS = 255 core，缩减比例：60.7%
- L21: ### [https://ego-portal.mlp.shopee.io/training/periodRule/2463/detail/info?current=1&pageSize=10&tab=jobs](https://ego-portal.mlp.shopee.io/training/periodRule/2463/detail/info?current=1&pageSize=10&tab=jobs)(完成迁移)
- L23: #### 带SS优化的镜像：[https://ego-portal.mlp.shopee.io/training/job/30178665/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30178665/detail/info?tab=task)
- L25: #### 不带SS优化的镜像：[https://ego-portal.mlp.shopee.io/training/job/30056702/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30056702/detail/info?tab=task)
- L27: #### 资源收益：缩减12个SS = 180 core，缩减比例：50%
- L29: ### [https://ego-portal.mlp.shopee.io/training/periodRule/2452/detail/info?current=1&pageSize=10&tab=jobs](https://ego-portal.mlp.shopee.io/training/periodRule/2452/detail/info?current=1&pageSize=10&tab=jobs)(完成迁移)
- L31: #### 带SS优化的镜像：[https://ego-portal.mlp.shopee.io/training/job/30200549/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30200549/detail/info?tab=task)
- L33: #### 带SS优化的镜像，并调整read_threads：[https://ego-portal.mlp.shopee.io/training/job/30525103/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30525103/detail/info?tab=task)
- L35: #### 不带SS优化的镜像：[https://ego-portal.mlp.shopee.io/training/job/30198997/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30198997/detail/info?tab=task)
- L37: #### 资源收益：缩减10个SS = 150 core，缩减比例：50%
- L39: ### [https://ego-portal.mlp.shopee.io/training/periodRule/1284/detail/info?current=1&pageSize=10&tab=jobs](https://ego-portal.mlp.shopee.io/training/periodRule/1284/detail/info?current=1&pageSize=10&tab=jobs)(已使用SS优化)
- L41: #### 用户当前使用的镜像：[https://ego-portal.mlp.shopee.io/training/job/30253725/detail/basic](https://ego-portal.mlp.shopee.io/training/job/30253725/detail/basic)
- L43: #### 一定带SS优化的镜像：[https://ego-portal.mlp.shopee.io/training/job/30508154/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30508154/detail/info?tab=task)
- L45: #### 不带SS优化的镜像：[https://ego-portal.mlp.shopee.io/training/job/30274899/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30274899/detail/info?tab=task)
- L47: #### 资源收益：缩减8个SS = 120 core，缩减比例：50%
- L49: ### [https://ego-portal.mlp.shopee.io/training/periodRule/1370/detail/info?current=1&pageSize=10&tab=jobs](https://ego-portal.mlp.shopee.io/training/periodRule/1370/detail/info?current=1&pageSize=10&tab=jobs)(已使用SS优化)
- L51: #### 用户当前使用的镜像：[https://ego-portal.mlp.shopee.io/training/job/30320891/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30320891/detail/info?tab=task)
- L53: #### 一定带SS优化的镜像：[https://ego-portal.mlp.shopee.io/training/job/30507994/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30507994/detail/info?tab=task)
- L55: #### 一定带SS优化的镜像，并调整read_threads：[https://ego-portal.mlp.shopee.io/training/job/30505085/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30505085/detail/info?tab=task)
- L57: #### 不带SS优化的镜像：[https://ego-portal.mlp.shopee.io/training/job/30318086/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30318086/detail/info?tab=task)
- L59: #### 资源收益：缩减7个SS = 105 core，缩减比例：23.4%
- L61: ### [https://ego-portal.mlp.shopee.io/training/periodRule/2517/detail/info?current=1&pageSize=10&tab=jobs](https://ego-portal.mlp.shopee.io/training/periodRule/2517/detail/info?current=1&pageSize=10&tab=jobs)(已使用SS优化)
- L63: #### 用户当前使用的镜像：[https://ego-portal.mlp.shopee.io/training/job/30321271/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30321271/detail/info?tab=task)
- L65: #### 一定带SS优化的镜像：[https://ego-portal.mlp.shopee.io/training/job/30499848/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30499848/detail/info?tab=task)
- L67: #### 一定带SS优化的镜像，并调整read_threads：[https://ego-portal.mlp.shopee.io/training/job/30501415/detail/info?tab=monitor](https://ego-portal.mlp.shopee.io/training/job/30501415/detail/info?tab=monitor)
- L69: #### 不带SS优化的镜像：[https://ego-portal.mlp.shopee.io/training/job/30385978/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30385978/detail/info?tab=task)
- L71: #### 资源收益：缩减26个SS = 390 core，缩减比例：50%
- L73: ### [https://ego-portal.mlp.shopee.io/training/periodRule/2221/detail/info?current=1&pageSize=10&tab=jobs](https://ego-portal.mlp.shopee.io/training/periodRule/2221/detail/info?current=1&pageSize=10&tab=jobs)(已使用SS优化)
- L75: #### 用户当前使用的镜像：[https://ego-portal.mlp.shopee.io/training/job/30395290/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30395290/detail/info?tab=task)
- L77: #### 一定带SS优化的镜像：[https://ego-portal.mlp.shopee.io/training/job/30496490/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30496490/detail/info?tab=task)
- L79: #### 一定带SS优化的镜像，并调整read_threads：[https://ego-portal.mlp.shopee.io/training/job/30496584/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30496584/detail/info?tab=task)
- L81: #### 不带SS优化的镜像：[https://ego-portal.mlp.shopee.io/training/job/30395295/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30395295/detail/info?tab=task)
- L83: #### 资源收益：缩减28个SS = 420 core，缩减比例：50%
- L85: ### [https://ego-portal.mlp.shopee.io/training/periodRule/2058/detail/info?current=1&pageSize=10&tab=jobs](https://ego-portal.mlp.shopee.io/training/periodRule/2058/detail/info?current=1&pageSize=10&tab=jobs)(已使用SS优化)
- L87: #### 用户当前使用的镜像：[https://ego-portal.mlp.shopee.io/training/job/30426040/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30426040/detail/info?tab=task)
- L89: #### 一定带SS优化的镜像：[https://ego-portal.mlp.shopee.io/training/job/30491382/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30491382/detail/info?tab=task)
- L91: #### 一定带SS优化的镜像，并调整read_threads：[https://ego-portal.mlp.shopee.io/training/job/30491390/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30491390/detail/info?tab=task)
- L93: #### 不带SS优化的镜像：[https://ego-portal.mlp.shopee.io/training/job/30426990/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30426990/detail/info?tab=task)
- L95: #### 资源收益：缩减32个SS = 480 core，缩减比例：50%
- L97: ### [https://ego-portal.mlp.shopee.io/training/periodRule/1442/detail/info?current=1&pageSize=10&tab=jobs](https://ego-portal.mlp.shopee.io/training/periodRule/1442/detail/info?current=1&pageSize=10&tab=jobs)(已使用SS优化)
- L99: #### 用户当前使用的镜像：[https://ego-portal.mlp.shopee.io/training/job/30431184/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30431184/detail/info?tab=task)
- L101: #### 一定带SS优化的镜像：[https://ego-portal.mlp.shopee.io/training/job/30456838/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30456838/detail/info?tab=task)
- L103: #### 一定带SS优化的镜像，并调整read_threads：[https://ego-portal.mlp.shopee.io/training/job/30465482/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30465482/detail/info?tab=task)
- L105: #### 不带SS优化的镜像：[https://ego-portal.mlp.shopee.io/training/job/30431262/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30431262/detail/info?tab=task)
- L107: #### 资源收益：缩减30个SS = 450 core，缩减比例：50%
- L109: ### 总结：

## `SS优化_收益统计 Ads.md` (12KB, 125行, 49节)

- L3: # PaidAds Rough Rank (V1.8.0):
- L5: ## 训练任务：
- L7: #### 带SS优化镜像（Custom 镜像为了支持cpp_data_converter新功能：[harbor.shopeemobile.com/mlp-ego/ego-train-runtime:Vtest-master-zjz-tf1-sg-20250303122427-ss-optim-cpp-final](http://harbor.shopeemobile.com/mlp-ego/ego-train-runtime:Vtest-master-zjz-tf1-sg-20250303122427-ss-optim-cpp-final)
- L9: #### 使用了不带SS优化的任务：[https://ego-portal.mlp.shopee.io/training/job/30154726/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30154726/detail/info?tab=task)
- L11: #### 使用了带SS优化的任务：[https://ego-portal.mlp.shopee.io/training/job/30241683/detail/info?tab=monitor](https://ego-portal.mlp.shopee.io/training/job/30241683/detail/info?tab=monitor)
- L13: #### 使用了带SS优化 + cpp_data_converter 的任务：[https://ego-portal.mlp.shopee.io/training/job/30286915/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30286915/detail/info?tab=task)
- L15: #### 使用了带SS优化 + cpp_data_converter 的任务 + read_thread=100 : [https://ego-portal.mlp.shopee.io/training/job/30456849/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30456849/detail/info?tab=task)
- L17: #### 使用python_converter的任务：[https://ego-portal.mlp.us.shopee.io/training/job/2363911/detail/info?tab=task](https://ego-portal.mlp.us.shopee.io/training/job/2363911/detail/info?tab=task)
- L19: #### 使用cpp_data_converter的任务：[https://ego-portal.mlp.us.shopee.io/training/job/2363508/detail/info?tab=task](https://ego-portal.mlp.us.shopee.io/training/job/2363508/detail/info?tab=task), [https://ego-portal.mlp.us.shopee.io/training/job/2364188/detail/info?tab=task](https://ego-portal.mlp.us.shopee.io/training/job/2364188/detail/info?tab=task), [https://ego-portal.mlp.us.shopee.io/training/job/2364421/detail/info?tab=task](https://ego-portal.mlp.us.shopee.io/training/job/2364421/detail/info?tab=task)
- L21: #### python_converter→cpp_data_converter的收益
- L26: #### 资源收益：缩减6个SS = 180 core
- L30: # PaidAds CR：
- L32: ## 训练任务：
- L36: #### 用户自己的任务：[https://ego-portal.mlp.shopee.io/training/job/30689787/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30689787/detail/info?tab=task)
- L38: #### 使用了不带SS优化的任务：[https://ego-portal.mlp.shopee.io/training/job/30739228/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30739228/detail/info?tab=task)
- L40: #### 使用了带SS优化的任务同等资源：[https://ego-portal.mlp.shopee.io/training/job/30742350/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30742350/detail/info?tab=task)
- L42: #### 使用了带SS优化的任务：[https://ego-portal.mlp.shopee.io/training/job/30769859/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30769859/detail/info?tab=task)
- L44: #### 使用了带SS优化的任务 + cpp_converter：[https://ego-portal.mlp.shopee.io/training/job/30771883/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30771883/detail/info?tab=task)
- L46: #### 使用python_converter的任务：[https://ego-portal.mlp.us.shopee.io/training/job/2364867/detail/info?tab=monitor](https://ego-portal.mlp.us.shopee.io/training/job/2364867/detail/info?tab=monitor)
- L48: #### 使用cpp_data_converter的任务：[https://ego-portal.mlp.us.shopee.io/training/job/2372696/detail/info?tab=task](https://ego-portal.mlp.us.shopee.io/training/job/2372696/detail/info?tab=task), [https://ego-portal.mlp.us.shopee.io/training/job/2373001/detail/info?tab=monitor](https://ego-portal.mlp.us.shopee.io/training/job/2373001/detail/info?tab=monitor)
- L50: #### python_converter→cpp_data_converter的收益
- L55: #### 资源收益：缩减5个SS = 150 core
- L59: # PaidAds Recall:
- L61: ## 训练任务：search Q2Q  (V1.8.0)
- L65: #### 带SS优化镜像：[harbor.shopeemobile.com/mlp-ego/ego-train-runtime:V1.8.2-dev-609c7b8f-tf2-sg-20250425091843](http://harbor.shopeemobile.com/mlp-ego/ego-train-runtime:V1.8.2-dev-609c7b8f-tf2-sg-20250425091843)
- L67: #### 用户自己的任务：[https://ego-portal.mlp.shopee.io/training/job/30129696/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30129696/detail/info?tab=task)
- L69: #### 使用了不带SS优化的任务：[https://ego-portal.mlp.shopee.io/training/job/31171554/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/31171554/detail/info?tab=task)
- L71: #### 使用了带SS优化的任务：[https://ego-portal.mlp.shopee.io/training/job/31635757/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/31635757/detail/info?tab=task)
- L73: #### 资源收益：缩减3个core
- L77: ## 训练任务：Discovery LTR (V1.8.0)
- L79: #### 带SS优化镜像：[harbor.shopeemobile.com/mlp-ego/ego-train-runtime:V1.8.2-dev-609c7b8f-tf1-sg-20250425091843](http://harbor.shopeemobile.com/mlp-ego/ego-train-runtime:V1.8.2-dev-609c7b8f-tf1-sg-20250425091843)
- L81: #### 用户自己的任务：[https://ego-portal.mlp.shopee.io/training/job/30899327/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30899327/detail/info?tab=task)
- L83: #### 使用了带SS优化的任务同等资源：[https://ego-portal.mlp.shopee.io/training/job/30919846/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30919846/detail/info?tab=task)
- L85: #### 使用了带SS优化的任务：[https://ego-portal.mlp.shopee.io/training/job/31572654/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/31572654/detail/info?tab=task)
- L87: #### 使用了带SS优化的任务 + cpp_converter：[https://ego-portal.mlp.shopee.io/training/job/30955884/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/30955884/detail/info?tab=task)
- L89: #### 资源收益：缩减2个SS = 32 core
- L93: # PaidAds Brand & Content:
- L95: ## 训练任务：pCTR_fusion_update (V1.8.0)
- L99: #### 带SS优化镜像：[harbor.shopeemobile.com/mlp-ego/ego-train-runtime:V1.8.2-dev-609c7b8f-tf2-sg-20250425091843](http://harbor.shopeemobile.com/mlp-ego/ego-train-runtime:V1.8.2-dev-609c7b8f-tf2-sg-20250425091843)
- L101: #### 用户自己的任务：[https://ego-portal.mlp.shopee.io/training/job/31332882/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/31332882/detail/info?tab=task)
- L103: #### 使用了不带SS优化的任务：[https://ego-portal.mlp.shopee.io/training/job/31373073/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/31373073/detail/info?tab=task)
- L105: #### 使用了带SS优化的任务：[https://ego-portal.mlp.shopee.io/training/job/31373077/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/31373077/detail/info?tab=task)
- L107: #### 资源收益：缩减2个SS = 48 core
- L111: ## 训练任务：ESMM (V1.8.0)
- L113: #### 带SS优化镜像：[harbor.shopeemobile.com/mlp-ego/ego-train-runtime:V1.8.2-tf1-sg-20250508072019](http://harbor.shopeemobile.com/mlp-ego/ego-train-runtime:V1.8.2-tf1-sg-20250508072019)
- L115: #### 使用了不带SS优化的任务：[https://ego-portal.mlp.shopee.io/training/job/31459304/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/31459304/detail/info?tab=task)
- L117: #### 使用了带SS优化的任务同等资源：[https://ego-portal.mlp.shopee.io/training/job/31508689/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/31508689/detail/info?tab=task)
- L119: #### 使用了带SS优化的任务: [https://ego-portal.mlp.shopee.io/training/job/31568953/detail/info?tab=task](https://ego-portal.mlp.shopee.io/training/job/31568953/detail/info?tab=task)
- L121: #### 资源收益：缩减7个SS = 224 core

## `Scripts for using EgoPortal API.md` (44KB, 408行, 99节)

- L1: ## Show help for any script
- L5: ## Launching
- L7: ### create_model.sh --tenant_name=${tenant_name} --project_name=${project_name} --model_name=${model_name} --model_desc=${model_desc:-"test"} --cluster_region=${cluster_region:-"sg"}
- L11: ##### Param:
- L18: ##### Return:
- L21: ##### Example:
- L23: ### create_model_version.sh --model_id=${model_id} --model_path=${model_path} --entry_file=${entry_file} --model_version_name=${model_version_name} --model_version_desc=${model_version_desc:-"test"} --git_path=${git_path:-""} --git_branch=${git_branch:-""} --git_commit_id=${git_commit_id:-""} --cluster_region=${cluster_region:-"sg"}
- L27: ##### Param:
- L38: ##### Return:
- L41: ##### Example:
- L43: ### launch_job.sh --job_name=${job_name} --model_id=${model_id} --model_version_id=${model_version_id} --ego_learner_file_path=${ego_learner_file_path} --running_files_dir=${running_files_dir} --description=${description} --worker_num=${worker_num} --worker_core=${worker_core:-10} --worker_mem=${worker_mem:-40} --sample_server_num=${sample_server_num:-3} --sample_server_core=${sample_server_core:-8} --sample_server_mem=${sample_server_mem:-40} --coordinator_core=${coordinator_core:-5} --coordinator_mem=${coordinator_mem:-10} --tags=${tags:-""} --checkpoint_id=${checkpoint_id:-0} --job_priority=${job_priority:-0} --filter_or_load=${filter_or_load:-0} --slots_list=${slots_list:-""} --skip_dnn_params=${skip_dnn_params:-0} --clear_nn_g2sum=${clear_nn_g2sum:-0} --user_define_hdfs_path=${user_define_hdfs_path:-""} --user_define_hdfs_prefix=${user_define_hdfs_prefix:-""} --user_define_filter_or_load=${user_define_filter_or_load:-0} --user_define_slots_list=${user_define_slots_list:-""} --user_define_skip_dnn_params=${user_define_skip_dnn_params:-0} --image=${image:-""} --initialize_script=${initialize_script:-""} --job_type=${job_type:-"train"} --kafka_group_id=${kafka_group_id:-""} --flag_file=${flag_file:-""} --kill_zombie_task=${kill_zombie_task:-1} --low_utilization_time_duration=${low_utilization_time_duration:-30} --low_utilization_cpu_threshold=${low_utilization_cpu_threshold:-0.01} --low_utilization_mem_threshold=${low_utilization_mem_threshold:-0.01} --kill_low_utilization_task=${kill_low_utilization_task:-0} --greedy_loading_mode=${greedy_loading_mode:-0} --offline_half_precision=${offline_half_precision:-1} --online_half_precision=${online_half_precision:-0} --is_colocate=${is_colocate:-0} --gpu_type=${gpu_type:-""} --mig_gpu=${mig_gpu:-""} --cluster_region=${cluster_region:-"sg"} --use_new_io=${use_new_io:-0}
- L47: ##### Param:
- L95: ##### Return:
- L98: ##### Example:
- L100: ## Enquiring
- L102: ### get_batch_platform_info.sh --cluster_region=${cluster_region:-"sg"}
- L106: ##### Param:
- L109: ##### Return:
- L111: ##### Example:
- L113: ### get_tag_enums.sh --cluster_region=${cluster_region:-"sg"}
- L117: ##### Param:
- L120: ##### Return:
- L122: ##### Example:
- L124: ### get_job_status_enums.sh --cluster_region=${cluster_region:-"sg"}
- L128: ##### Param:
- L131: ##### Return:
- L133: ##### Example:
- L135: ### get_job_status.sh --job_id=${job_id} --verbose=${verbose:-0} --cluster_region=${cluster_region:-"sg"}
- L139: ##### param:
- L146: ##### Return:
- L148: ##### Example:
- L150: ### get_model_list.sh --project_name=${project_name:-""} --model_name=${model_name:-""} --page_id=${page_id:-1} --verbose=${verbose:-0} --account=${account:2} --cluster_region=${cluster_region:-"sg"}
- L154: ##### Param:
- L161: ##### Return:
- L163: ##### Example:
- L165: ### get_model_version_list.sh --model_id=${model_id} --model_version_name=${model_version_name:-""} --page_id=${page_id:-1} --verbose=${verbose:-0} --cluster_region=${cluster_region:-"sg"}
- L169: ##### Param:
- L176: ##### Return:
- L178: ##### Example:
- L180: ### get_job_list.sh --model_version_id=${model_version_id} --job_status=${job_status:-""} --tags=${tags:-""} --page_id=${page_id:-1} --online_learning_job_list=${online_learning_job_list:-1} --cluster_region=${cluster_region:-"sg"}
- L184: ##### Param:
- L192: ##### Return:
- L194: ##### Example:
- L196: ### get_checkpoint_list.sh --model_id=${model_id} --model_version_id=${model_version_id} --page_id=${page_id:-1} --cluster_region=${cluster_region:-"sg"}
- L200: #####  Param:
- L206: ##### Return:
- L210: ##### Example:
- L212: ### get_job_metrics.sh --job_id=${job_id} --metric_duration=${metric_duration:-"hour"} --round_name=${round_name:-""} --target_name=${target_name:-""} --cluster_region=${cluster_region:-"sg"}
- L221: ## Deleting
- L223: ### delete_model.sh --model_id=${model_id} --cluster_region=${cluster_region:-"sg"}
- L227: ##### Param:
- L231: ##### Return:
- L233: ##### Example:
- L235: ### delete_model_version.sh --model_id=${model_id} --model_version_id=${model_version_id} --cluster_region=${cluster_region:-"sg"}
- L239: ##### Param:
- L244: ##### Return:
- L246: ##### Example:
- L248: ### stop_job.sh --job_id=${job_id} --cluster_region=${cluster_region:-"sg"}
- L252: ##### Param:
- L256: ##### Return:
- L258: ##### Example:
- L260: ### delete_job.sh --job_id=${job_id} --cluster_region=${cluster_region:-"sg"}
- L264: ##### Param:
- L268: ##### Return:
- L270: ##### Example:
- L272: ### delete_checkpoint.sh --checkpoint_id=${checkpoint_id} --cluster_region=${cluster_region:-"sg"}
- L276: ##### Param:
- L280: ##### Return:
- L282: ##### Example:
- L284: ## Publishing
- L286: ### get_online_model_list.sh --online_model_name=${online_model_name:-""} --tenant_name=${tenant_name:-""} --project_name=${project_name:-""} --page_id=${page_id:-1} --verbose=${verbose:-0} --account=${account:-2} --offline_model_version_id=${offline_model_version_id:-""} --online_model_type=${online_model_type:-0} --cluster_region=${cluster_region:-"sg"}
- L290: ##### Param:
- L301: ##### Return:
- L303: ##### Example:
- L305: ### get_online_job_list.sh --online_model_id=${online_model_id} --job_status=${job_status:-""} --page_id=${page_id:-1} --cluster_region=${cluster_region:-"sg"}
- L309: ##### Param:
- L315: ##### Return:
- L317: ##### Example:
- L319: ### publish_model.sh --model_id=${model_id} --model_version_id=${model_version_id} --checkpoint_id=${checkpoint_id} --online_model_name=${online_model_name} --fg_dir=${fg_dir} --model_json=${model_json} --online_export_yaml=${online_export_yaml} --target_project=${target_project:-""} --online_model_desc=${online_model_desc:-""} --online_converter_stable=${online_converter_stable:-""} --image=${image:-""} --online_compile_config_file=${online_compile_config_file:""} --release_to_live=${release_to_live:-1} --half_precision=${half_precision:0} --job_type=${job_type:0} --online_learning_job_id=${online_learning_job_id:""} --sync_frequency=${sync_frequency:600} --grey_release=${grey_release:-0} --grey_release_precentage=${grey_release_precentage:-10} --model_conf_json=${model_conf_json:-""} --cluster_region=${cluster_region:-"sg"}
- L323: ##### Param:
- L348: ##### Return:
- L350: ##### Example:
- L352: ## Auxiliary tools
- L354: ### pull_log.sh --tenant_name=${tenant_name} --project_name=${project_name} --job_id=${job_id} --cluster_region=${cluster_region:-"sg"}
- L358: ##### Param:
- L364: ##### Return:
- L366: ##### Example:
- L368: ### move_model.sh --model_name=${model_name} --target_project_name=${target_project_name} --cluster_region=${cluster_region:-"sg"}
- L372: ##### Param:
- L377: ##### Return:
- L379: ##### Example:
- L381: ### local_compile.sh --model_path=${model_path} --entry_file=${entry_file} --image=${image:-""} --cluster_region=${cluster_region:-"sg"}
- L385: ##### Param:
- L391: ##### Return:
- L393: ##### Example:
- L395: ### sync_checkpoint.sh --target_model_id=${target_model_id} --target_model_version_id=${target_model_version_id} --checkpoint_id=${checkpoint_id} --source_cluster=${source_cluster} --target_cluster=${target_cluster}
- L399: ##### Param:
- L406: ##### Return:
- L408: ##### Example:

## `TF fp16离线测试结果.md` (11KB, 48行, 5节)

- L1: # 一.gpu pdp离线测试结果
- L8: # 二.gpu cart离线测试结果
- L12: # 三.gpu dd离线测试结果
- L20: # 四.测试结论
- L42: # 五.开启tf fp16的方法

## `Tutorial of EGO V1_0.md` (12KB, 197行, 25节)

- L7: #### generate compiled files
- L18: #### advanced features
- L23: ##### advanced features in sparse embeddings
- L25: ###### customise sparse embedding's config in different slots
- L33: ###### share embeddings among multiple slots
- L39: ###### set up feature admission and evict
- L45: ###### config adf segment in sparse embeddings (feature statistics)
- L68: ###### caching tensor in offline training for reducing computations in online service
- L72: ##### advanced features in neural networks
- L74: ###### different normalisation layer
- L78: ###### customise optimisers for each layer
- L82: #### Attention
- L89: ### model-run
- L115: ### Running custom ego-train-v1 build in notebook
- L147: ## ego-ps
- L154: ### Optimizers in ego-ps
- L159: ## ego-predictor
- L165: ## ego-controller
- L169: ### EgoPortal
- L175: #### Organise files in right way
- L179: #### Submit a training job
- L183: #### Publish a well-trained model
- L187: ### EgoScheduler
- L191: ### EgoSupervisor
- L195: ### [A demo of overall steps from submitting a training job to publishing the model](https://confluence.shopee.io/display/MLP/DeepCtr+Demo)

## `Variable embedding length survey.md` (13KB, 27行, 4节)

- L1: ## Basic idea
- L7: ## Paper's experiment result
- L13: ## Work to do to implement it in Ego
- L24: ## Coarse simulation to testify the idea in Ego

## `[A]Ego New Member Guide(used by EGO members internally).md` (14KB, 175行, 21节)

- L1: ## I. Note (说明)
- L19: ## II. Main platforms and systems(主要平台和系统)
- L21: ## bj开发机使用
- L29: ## sg开发机使用
- L37: ## III. Permission Application(权限申请)
- L39: ### Serving CMDB Permissions(Serving CMDB 权限)
- L58: ### TOC Permissions（TOC 权限）
- L68: ### SAM Permissions
- L72: ### DMP Permissions（DMP 权限）
- L78: ### Confluence Group Permission
- L84: ## IV. EGO platform basic information(EGO平台基本信息)
- L104: ## Ⅴ. FAQ
- L106: ### 1. What do the various abbreviations mean? (各种缩写代表什么含义？)
- L113: ### 2. Development machines can not access git.garena.com ?(开发机和 git.garena.com 不通？)
- L119: ### 3. The development machine cannot use VS Code's remote ssh connection? (开发机无法使用 VS Ccode 的 remote ssh 连接？)
- L133: ### 4. If there is a timeout when logging in to the develop machine(ERROR_SERVER_CONNECTION_TIMEOUT), please try a few more times.
- L137: ### 5. How to install spark/hadoop in toc machines?
- L141: ### 6. How to break down the limitation of network when transferring between development machines and local Mac?
- L149: ### 7. How to apply for Hadoop Permission?
- L161: ### 8. How to run Spark Job?
- L175: ### 8. How to run Spark Job?

## `config module_ ego-learner_yaml.md` (24KB, 136行, 6节)

- L29: #### seperate data source config
- L43: ## train config
- L110: ## eval config
- L118: ## eval fea config
- L125: ## nsc config
- L129: ## metric config

## `python worker.md` (15KB, 99行, 20节)

- L1: # What is Python worker
- L5: # How to use Python worker
- L7: ## Adapt your model
- L16: ## Run your model in cluster
- L24: # Train/debug your model in local machine
- L33: ## Running with ps
- L37: ### Manually start a ps cluster with shard_num is 1
- L39: ### Connect to ps cluster
- L44: ## Use io.limit_minibatch_num to limit how many batches will sample server read
- L48: # Examples
- L50: ## Learning rate schedule
- L55: ## Use metric result
- L60: ## Fetch gradient/embedding with training
- L75: ## Report user self defined metric to grafana
- L77: ## Trigger Dump/Evict for PS manually
- L80: ## Get PS model stat info
- L83: # API
- L85: ## ego.Learner
- L89: ## py_ego_core.SlotCategory
- L94: ## py_ego_core.BatchFea

## `trt_backend vs xla_backend vs tf_backend 性能对比.md` (14KB, 383行, 36节)

- L3: ## EgoTrain离线测试
- L5: ### Order Guarantee project的实验模型 (小模型)
- L7: #### tf_backend
- L21: #### xla_backend
- L33: #### trt_backend
- L35: ##### TF32精度+cuda_graph优化
- L51: ##### TF32精度
- L65: ### 搜索dsrm_v5_5_2_opt模型
- L67: #### tf_backend:
- L81: #### xla_backend:
- L95: #### trt_backend
- L97: ##### TF32精度+cuda_graph优化
- L111: ##### TF32精度
- L125: ##### FP16精度+cuda_graph优化
- L139: ##### FP16精度
- L153: ##### TF32精度+cuda_graph优化+graph_final.pb
- L167: ##### TF32精度+graph_final.pb
- L181: ##### FP16精度+graph_final.pb
- L195: ##### FP16精度+cuda_graph+graph_final.pb
- L209: ### pdp cart ID区域cvr模型
- L211: #### tf_backend
- L225: #### xla_backend
- L239: #### trt_backend
- L241: ##### TF32精度+cuda_graph优化
- L263: ##### TF32精度
- L277: ##### FP16精度+cuda_graph优化
- L291: ##### FP16精度
- L305: ##### TF32精度+cuda_graph优化+graph_final.pb
- L319: ##### TF32精度+graph_final.pb
- L337: ##### FP16精度+cuda_graph优化+graph_final.pb
- L351: ##### FP16精度+graph_final.pb
- L365: ## EgoPredictor在线测试
- L367: ### pdp cart ID区域cvr模型
- L371: #### xla_backend
- L373: #### trt_backend
- L377: ## Conclusion

## `以太网 vs rdma性能测试.md` (12KB, 59行, 14节)

- L1: # dsrm_v70
- L3: ## 单网卡50Gbps测试结果
- L7: ## 双网卡100Gbps测试结果
- L12: # dsrm_v552
- L16: ## 单网卡50Gbps测试结果
- L20: ## 双网卡100Gbps测试结果
- L24: ## 单网卡50Gbps性能分析
- L36: # cvr_v21_delay_br
- L38: ## 双网卡100Gbps测试结果
- L42: # cvr_new_model_v31
- L44: ## 双网卡100Gbps测试结果
- L48: # attv_brd_ltr_index
- L50: ## 双网卡100Gbps测试结果
- L55: # 结论

## `调研_通过SPDK tool来管理nvme磁盘.md` (13KB, 235行, 101节)

- L1: ##### 随机写(DirectIO, 2.23GB/s): `fio --name=randwrite --ioengine=sync --rw=randwrite --bs=22m --direct=1 --size=10G --filename=testfile`
- L3: ##### 随机写(DirectIO, 2.24GB/s): `fio --name=randwrite --ioengine=psync --rw=randwrite --bs=22m --direct=1 --size=10G --filename=testfile`
- L5: ##### 顺序写(DirectIO, 2.24GB/s): `fio --name=write --ioengine=libaio --rw=write --bs=22m --direct=1 --size=10G --filename=testfile`
- L7: ##### 顺序写(DirectIO, 2.22GB/s): `fio --name=write --ioengine=sync --rw=write --bs=22m --direct=1 --size=10G --filename=testfile`
- L9: ##### 顺序写(DirectIO, 2.23GB/s): `fio --name=write --ioengine=psync --rw=write --bs=22m --direct=1 --size=10G --filename=testfile`
- L11: ##### 随机读(DirectIO, 5.375GB/s): `fio --name=randread --ioengine=libaio --rw=randread --bs=22m --direct=1 --size=10G --filename=testfile`
- L13: ##### 随机读(DirectIO, 5.38GB/s): `fio --name=randread --ioengine=sync --rw=randread --bs=22m --direct=1 --size=10G --filename=testfile`
- L15: ##### 随机读(DirectIO, 5.35GB/s): `fio --name=randread --ioengine=psync --rw=randread --bs=22m --direct=1 --size=10G --filename=testfile`
- L17: ##### 顺序读(DirectIO, 5.36GB/s): `fio --name=read --ioengine=libaio --rw=read --bs=22m --direct=1 --size=10G --filename=testfile`
- L19: ##### 顺序读(DirectIO, 5.36GB/s): `fio --name=read --ioengine=sync --rw=read --bs=22m --direct=1 --size=10G --filename=testfile`
- L21: ##### 顺序读(DirectIO, 5.39GB/s): `fio --name=read --ioengine=psync --rw=read --bs=22m --direct=1 --size=10G --filename=testfile`
- L23: ##### 随机写(1.87GB/s): `fio --name=randwrite --ioengine=libaio --rw=randwrite --bs=22m --direct=0 --size=10G --filename=testfile`
- L25: ##### 随机写(1.77GB/s): `fio --name=randwrite --ioengine=sync --rw=randwrite --bs=22m --direct=0 --size=10G --filename=testfile`
- L27: ##### 随机写(1.53GB/s): `fio --name=randwrite --ioengine=psync --rw=randwrite --bs=22m --direct=0 --size=10G --filename=testfile`
- L29: ##### 顺序写(1.89GB/s): `fio --name=write --ioengine=libaio --rw=write --bs=22m --direct=0 --size=10G --filename=testfile`
- L31: ##### 顺序写(1.88GB/s): `fio --name=write --ioengine=sync --rw=write --bs=22m --direct=0 --size=10G --filename=testfile`
- L33: ##### 顺序写(1.58GB/s): `fio --name=write --ioengine=psync --rw=write --bs=22m --direct=0 --size=10G --filename=testfile`
- L35: ##### 随机读(520MB/s): `fio --name=randread --ioengine=libaio --rw=randread --bs=22m --direct=0 --size=10G --filename=testfile`
- L37: ##### 随机读(559MB/s): `fio --name=randread --ioengine=sync --rw=randread --bs=22m --direct=0 --size=10G --filename=testfile`
- L39: ##### 随机读(570MB/s): `fio --name=randread --ioengine=psync --rw=randread --bs=22m --direct=0 --size=10G --filename=testfile`
- L41: ##### 顺序读(1.07GB/s): `fio --name=read --ioengine=libaio --rw=read --bs=22m --direct=0 --size=10G --filename=testfile`
- L43: ##### 顺序读(1.17GB/s): `fio --name=read --ioengine=sync --rw=read --bs=22m --direct=0 --size=10G --filename=testfile`
- L45: ##### 顺序读(1.16GB/s): `fio --name=read --ioengine=psync --rw=read --bs=22m --direct=0 --size=10G --filename=testfile`
- L47: #### 限制cpu的使用率(--cpus=0.2)
- L49: ##### 随机写(DirectIO, 2.17GB/s): `fio --name=randwrite --ioengine=libaio --rw=randwrite --bs=22m --direct=1 --size=10G --filename=testfile`
- L51: ##### 随机写(DirectIO, 2.21GB/s): `fio --name=randwrite --ioengine=sync --rw=randwrite --bs=22m --direct=1 --size=10G --filename=testfile`
- L53: ##### 随机写(DirectIO, 2.19GB/s): `fio --name=randwrite --ioengine=psync --rw=randwrite --bs=22m --direct=1 --size=10G --filename=testfile`
- L55: ##### 顺序写(DirectIO, 2.22GB/s): `fio --name=write --ioengine=libaio --rw=write --bs=22m --direct=1 --size=10G --filename=testfile`
- L57: ##### 顺序写(DirectIO, 2.21GB/s): `fio --name=write --ioengine=sync --rw=write --bs=22m --direct=1 --size=10G --filename=testfile`
- L59: ##### 顺序写(DirectIO, 2.22GB/s): `fio --name=write --ioengine=psync --rw=write --bs=22m --direct=1 --size=10G --filename=testfile`
- L61: ##### 随机读(DirectIO, 4.95GB/s): `fio --name=randread --ioengine=libaio --rw=randread --bs=22m --direct=1 --size=10G --filename=testfile`
- L63: ##### 随机读(DirectIO, 5.17GB/s): `fio --name=randread --ioengine=sync --rw=randread --bs=22m --direct=1 --size=10G --filename=testfile`
- L65: ##### 随机读(DirectIO, 4.9GB/s): `fio --name=randread --ioengine=psync --rw=randread --bs=22m --direct=1 --size=10G --filename=testfile`
- L67: ##### 顺序读(DirectIO, 5.26GB/s): `fio --name=read --ioengine=libaio --rw=read --bs=22m --direct=1 --size=10G --filename=testfile`
- L69: ##### 顺序读(DirectIO, 5.17GB/s): `fio --name=read --ioengine=sync --rw=read --bs=22m --direct=1 --size=10G --filename=testfile`
- L71: ##### 顺序读(DirectIO, 5.08GB/s): `fio --name=read --ioengine=psync --rw=read --bs=22m --direct=1 --size=10G --filename=testfile`
- L73: ##### 随机写(369MB/s): `fio --name=randwrite --ioengine=libaio --rw=randwrite --bs=22m --direct=0 --size=10G --filename=testfile`
- L75: ##### 随机写(373MB/s): `fio --name=randwrite --ioengine=sync --rw=randwrite --bs=22m --direct=0 --size=10G --filename=testfile`
- L77: ##### 随机写(353MB/s): `fio --name=randwrite --ioengine=psync --rw=randwrite --bs=22m --direct=0 --size=10G --filename=testfile`
- L79: ##### 顺序写(368MB/s): `fio --name=write --ioengine=libaio --rw=write --bs=22m --direct=0 --size=10G --filename=testfile`
- L81: ##### 顺序写(361MB/s): `fio --name=write --ioengine=sync --rw=write --bs=22m --direct=0 --size=10G --filename=testfile`
- L83: ##### 顺序写(370MB/s): `fio --name=write --ioengine=psync --rw=write --bs=22m --direct=0 --size=10G --filename=testfile`
- L85: ##### 随机读(436MB/s): `fio --name=randread --ioengine=libaio --rw=randread --bs=22m --direct=0 --size=10G --filename=testfile`
- L87: ##### 随机读(445MB/s): `fio --name=randread --ioengine=sync --rw=randread --bs=22m --direct=0 --size=10G --filename=testfile`
- L89: ##### 随机读(428MB/s): `fio --name=randread --ioengine=psync --rw=randread --bs=22m --direct=0 --size=10G --filename=testfile`
- L91: ##### 顺序读(429MB/s): `fio --name=read --ioengine=libaio --rw=read --bs=22m --direct=0 --size=10G --filename=testfile`
- L93: ##### 顺序读(434MB/s): `fio --name=read --ioengine=sync --rw=read --bs=22m --direct=0 --size=10G --filename=testfile`
- L95: ##### 顺序读(431MB/s): `fio --name=read --ioengine=psync --rw=read --bs=22m --direct=0 --size=10G --filename=testfile`
- L97: #### 限制cpu的使用率(--cpus=0.02)
- L99: ##### 随机写(DirectIO, 239MB/s): `fio --name=randwrite --ioengine=libaio --rw=randwrite --bs=22m --direct=1 --size=10G --filename=testfile`
- L101: ##### 随机写(DirectIO, 264MB/s): `fio --name=randwrite --ioengine=sync --rw=randwrite --bs=22m --direct=1 --size=10G --filename=testfile`
- L103: ##### 随机写(DirectIO, 308MB/s): `fio --name=randwrite --ioengine=psync --rw=randwrite --bs=22m --direct=1 --size=10G --filename=testfile`
- L105: ##### 顺序写(DirectIO, 272MB/s): `fio --name=write --ioengine=libaio --rw=write --bs=22m --direct=1 --size=10G --filename=testfile`
- L107: ##### 顺序写(DirectIO, 274MB/s): `fio --name=write --ioengine=sync --rw=write --bs=22m --direct=1 --size=10G --filename=testfile`
- L109: ##### 顺序写(DirectIO, 302MB/s): `fio --name=write --ioengine=psync --rw=write --bs=22m --direct=1 --size=10G --filename=testfile`
- L111: ##### 随机读(DirectIO, 396MB/s): `fio --name=randread --ioengine=libaio --rw=randread --bs=22m --direct=1 --size=10G --filename=testfile`
- L113: ##### 随机读(DirectIO, 384MB/s): `fio --name=randread --ioengine=sync --rw=randread --bs=22m --direct=1 --size=10G --filename=testfile`
- L115: ##### 随机读(DirectIO, 466MB/s): `fio --name=randread --ioengine=psync --rw=randread --bs=22m --direct=1 --size=10G --filename=testfile`
- L117: ##### 顺序读(DirectIO, 409MB/s): `fio --name=read --ioengine=libaio --rw=read --bs=22m --direct=1 --size=10G --filename=testfile`
- L119: ##### 顺序读(DirectIO, 382MB/s): `fio --name=read --ioengine=sync --rw=read --bs=22m --direct=1 --size=10G --filename=testfile`
- L121: ##### 顺序读(DirectIO, 426MB/s): `fio --name=read --ioengine=psync --rw=read --bs=22m --direct=1 --size=10G --filename=testfile`
- L123: ##### 随机写(43.1MB/s): `fio --name=randwrite --ioengine=libaio --rw=randwrite --bs=22m --direct=0 --size=10G --filename=testfile`
- L125: ##### 随机写(34.6MB/s): `fio --name=randwrite --ioengine=sync --rw=randwrite --bs=22m --direct=0 --size=10G --filename=testfile`
- L127: ##### 随机写(33.6MB/s): `fio --name=randwrite --ioengine=psync --rw=randwrite --bs=22m --direct=0 --size=10G --filename=testfile`
- L129: ##### 顺序写(33.9MB/s): `fio --name=write --ioengine=libaio --rw=write --bs=22m --direct=0 --size=10G --filename=testfile`
- L131: ##### 顺序写(33.7MB/s): `fio --name=write --ioengine=sync --rw=write --bs=22m --direct=0 --size=10G --filename=testfile`
- L133: ##### 顺序写(32MB/s): `fio --name=write --ioengine=psync --rw=write --bs=22m --direct=0 --size=10G --filename=testfile`
- L135: ##### 随机读(37MB/s): `fio --name=randread --ioengine=libaio --rw=randread --bs=22m --direct=0 --size=10G --filename=testfile`
- L137: ##### 随机读(34.9MB/s): `fio --name=randread --ioengine=sync --rw=randread --bs=22m --direct=0 --size=10G --filename=testfile`
- L139: ##### 随机读(38.1MB/s): `fio --name=randread --ioengine=psync --rw=randread --bs=22m --direct=0 --size=10G --filename=testfile`
- L141: ##### 顺序读(38.4MB/s): `fio --name=read --ioengine=libaio --rw=read --bs=22m --direct=0 --size=10G --filename=testfile`
- L143: ##### 顺序读(38.1MB/s): `fio --name=read --ioengine=sync --rw=read --bs=22m --direct=0 --size=10G --filename=testfile`
- L145: ##### 顺序读(41.1MB/s): `fio --name=read --ioengine=psync --rw=read --bs=22m --direct=0 --size=10G --filename=testfile`
- L147: ## SPDK(用户态驱动)
- L151: ### SPDK介绍
- L165: ### 编译流程
- L170: #### 编译fio
- L176: #### 编译spdk
- L182: ### 测试流程
- L184: #### 检查系统内核已经加载了uio_pci_generic用户驱动模块, 因为这个模块是在/lib下面，所以进入docker环境时需要挂载`-v /lib:/lib -v /dev:/dev --privilege`
- L186: #### 卸载nvme硬盘
- L190: #### 使用uio_pci_generic用户态驱动加载nvme硬盘
- L192: #### 编写fio文件
- L194: #### 执行spdk-fio测试
- L198: ### 测试结果
- L200: #### 充足cpu资源
- L202: ##### 随机写(DirectIO, 2.49GB/s)
- L204: ##### 顺序写(DirectIO, 2.47GB/s)
- L206: ##### 随机读(DirectIO, 3.4GB/s)
- L208: ##### 顺序读(DirectIO, 3.4GB/s)
- L210: #### 限制cpu的使用率(–cpus=0.2)
- L212: ##### 随机写(DirectIO, 2.02GB/s)
- L214: ##### 顺序写(DirectIO, 2.03GB/s)
- L216: ##### 随机读(DirectIO, 2.29GB/s)
- L218: ##### 顺序读(DirectIO, 2.34GB/s)
- L220: #### 限制cpu的使用率(--cpus=0.02)
- L222: ##### 随机写(DirectIO, 209MB/s)
- L224: ##### 顺序写(DirectIO, 211MB/s)
- L226: ##### 随机读(DirectIO, 1.31GB/s)
- L228: ##### 顺序读(DirectIO, 1.25GB/s)
- L230: ## 总结
