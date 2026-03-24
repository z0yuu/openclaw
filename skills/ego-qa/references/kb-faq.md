# EGO FAQ 路由（仅定位，非答案来源）

# 覆盖 526 篇 | 格式: 文件名|行范围|关键词

(Old)EgoTrain*User_Manual.md|L1-L4|hdfs requirements tensorflow version sample data model output should located
(Old)EgoTrain_User_Manual.md|L5-L16|ps release ss api sdk latest version please refer access
(Old)EgoTrain_User_Manual.md|L17-L20|ps dev machine now no apply special develop model submit
(Old)EgoTrain_User_Manual.md|L21-L24|samples more info organise sample data format please refer
(Old)EgoTrain_User_Manual.md|L25-L34|slot sparse dense feature text format sample_id x1 x2 onehot
(Old)EgoTrain_User_Manual.md|L35-L41|ps protobuf format ego_sample proto please refer definition pb_tools git
(Old)EgoTrain_User_Manual.md|L44-L80|ps compile release train download latest released ego sdk unpack
(Old)EgoTrain_User_Manual.md|L81-L88|deepctr emb embedding sparse ss hdfs build edit demo emb-build
(Old)EgoTrain_User_Manual.md|L89-L95|ckpt deepctr publish ss hdfs pack model related resources python
(Old)EgoTrain_User_Manual.md|L96-L102|ckpt serving slot publish ss hdfs pack model egotf serving_path
(Old)Ego_Design.md|L1-L5|gpu ss introduction ai technology deep learning core achieved great
(Old)Ego_Design.md|L6-L10|ps sparse feature background present industry several solutions large-scale features
(Old)Ego_Design.md|L11-L17|ps worker ss design ideas simple architecture plan put same
(Old)Ego_Design.md|L18-L22|framework use tensorflow training kernel perform feed-forward back-propagation openmpi collective
(Old)Ego_Design.md|L25-L28|format tfrecord text strongly suggest
(Old)Ego_Design.md|L29-L32|worker sample unit split samples block example mb one minimal
(Old)Ego_Design.md|L35-L38|samples without re-organization read batch train next memory
(Old)Ego_Design.md|L39-L52|ss re-organise samples day hour read all data one memory
(Old)Ego_Design.md|L55-L58|mode local validate debug cluster yarn multiple physical machines
(Old)Ego_Design.md|L59-L63|user preparation build tensorflow static graph yaml config files defined
(Old)Ego_Design.md|L66-L69|feature high auc lots tricks special features model generated under
(Old)Ego_Design.md|L70-L75|ss fast concept design things much possibly user just needs
(Old)Ego_Design.md|L76-L79|emb embedding sparse admittance kick-out control amount within suitable range
(Old)Ego_Design.md|L80-L83|sparse dense feature adf auto based accumulate using
(Old)Ego_Design.md|L84-L95|eval two stage training optional shuffle data globally sufficiently considering
(Old)Ego_Design.md|L96-L99|eval feature importance evaluation provide way check each
(Old)Ego_Design.md|L100-L103|ss incremental learning normally split one day passes minutes pass
(Old)Ego_Design.md|L104-L107|mig slot sparse feature min max avg sum pooling methods
(Old)Ego_Design.md|L108-L115|emb embedding sparse export zmap high performance key-value structure used
(Old)Ego_Design.md|L116-L119|ss shuffle samples one sample part file continual time user
(Old)Ego_Design.md|L124-L127|support many metrics such auc gauc user configure some optional
(Old)Ego_Design.md|L142-L145|deepctr ps demo git garena shopee-server dailydiscover ego-dlp blob master
(Old)Ego_Design.md|L146-L148|deepctr ps sparse ego-learner yaml config files sparsednn_2stage configuration git
01-basic-concept.md.md|L1-L5|模型 训练 emb 参数 embedding sparse worker ego_lite ss ego
01-basic-concept.md.md|L6-L13|样本 sparse 特征 dense feature sample format label weight uniq_id
01-basic-concept.md.md|L14-L17|slot emb embedding ego_lite 特征 slot_id fsign ego hash_slot_id feauture_name
01-basic-concept.md.md|L18-L20|模型 训练 sub model tf saved_model item user 任意 存在
02-begin-with-deepctr.ipynb.md|L31-L57|deepctr benchmark dense feature ss hdfs configure class object data_path
02-begin-with-deepctr.ipynb.md|L58-L124|sparse feature write dataset reader def parse_line_batch lines fea_desc example_id
02-begin-with-deepctr.ipynb.md|L125-L668|batch_size feature test dataset reader dates el utility expand_shell_pattern train_days
02-begin-with-deepctr.ipynb.md|L669-L716|ps slot emb embedding sparse feature create fetch layer def
02-begin-with-deepctr.ipynb.md|L717-L729|ps emb embedding feature test fetch dataset_iter iter dataset feature_dict
02-begin-with-deepctr.ipynb.md|L730-L743|deepctr ps emb sparse benchmark feature hdfs inlut data read
02-begin-with-deepctr.ipynb.md|L744-L964|ps emb because optimizer initiliazed embs all out tf tensor
02-begin-with-deepctr.ipynb.md|L965-L1213|predictor 模型 sparse create sub model exported oneself used model_conf
02-begin-with-deepctr.ipynb.md|L1216-L1224|ps sparse feature let constuct input feed sub model sparse_inputs
02-begin-with-deepctr.ipynb.md|L1225-L1232|ps emb embedding sparse dense feature get pooled sparse_emb_layer sparse_embs
02-begin-with-deepctr.ipynb.md|L1233-L1242|ps emb sparse dense let construct full model sub_model_output sub_model
02-begin-with-deepctr.ipynb.md|L1243-L1295|ps compile dense ss train model dense_opt el optimizer adamw
02-share-embedding.md.md|L10-L30|slot emb embedding sparse feature feature1 feature2 slot_id ec el
02-share-embedding.md.md|L34-L39|emb embedding 特征 f2 embedding_column 核心 注意 对于 两个 定义
03-training-in-cluster.md|L1-L4|wc 模型 ps 训练 worker basic concept cluster_solo_mode ps_solo_mode cluster
03-training-in-cluster.md|L5-L53|ps batch_size running model cluster def train dates el utility
03-training-in-cluster.md|L54-L57|模型 ps compile model dump_compiled_model config dump workspace code s3
03-training-in-cluster.md|L62-L65|样本 ego_lite train round model predict 步骤 没有 概念 用户
03-training-in-cluster.md|L66-L69|portal eval 任务 checkpoint evaluation 选择 加载 历史 预估 任何
03-training-in-cluster.md|L70-L72|predictor 配置 online_export submodel graph validate dump workspace code saved_model
09-how-to-get-sequence-embedding_md.md|L22-L42|predictor 模型 ps sparse ego_lite feature f2 tensor key tile_num
1_6_0 GPU pooling * dense allreduce与worker pooling性能对比测试.md|L3-L8|配置 训练 cpu 任务 a30 gpu 内存 soc tb pod
1*6_0 GPU pooling * dense allreduce与worker pooling性能对比测试.md|L9-L16|训练 cpu worker gpu c3v3 c3v2 机器 速度 置换 计算方法
1*6_0 GPU pooling * dense allreduce与worker pooling性能对比测试.md|L19-L44|portal 模型 ps 训练 emb batch*size ego-portal feature hdfs cart_feat_unify_v4_hinet_v2_emb_new22_t_1_br
1_6_0 GPU pooling * dense allreduce与worker pooling性能对比测试.md|L45-L46|mig 训练 cpu batch*size gpu c3_v3 c3_v2 g18_v3 g18 速度
1_6_0 GPU pooling * dense allreduce与worker pooling性能对比测试.md|L47-L68|portal 模型 ps batch*size benchmark ego-portal hdfs dd_din_lt_esmm_mpi_softsim_2k_cl_adf_mgdcn_v2_br live-test model
1_6_0 GPU pooling * dense allreduce与worker pooling性能对比测试.md|L69-L70|训练 cpu batch*size gpu c3_v3 c3_v2 g18_v3 速度 置换
1_6_0 GPU pooling * dense allreduce与worker pooling性能对比测试.md|L71-L92|portal 模型 ps batch*size ego-portal hdfs dsrm4_v5_ctr_prun_nn_t_5_l5 live-test model model_management
1_6_0 GPU pooling * dense allreduce与worker pooling性能对比测试.md|L93-L95|训练 cpu batch*size gpu c3_v3 c3_v2 g18_v3 速度 置换
1_6_0 GPU pooling * dense allreduce与worker pooling性能对比测试.md|L96-L107|train*threads cpu 任务 ego-train batch_size worker release gpu 资源 allreduce
1_6_0 GPU pooling * dense allreduce与worker pooling性能对比测试.md|L108-L109|训练 cpu batch*size gpu c3_v3 c3_v2 g18_v3 速度 置换
1_6_0 GPU pooling * dense allreduce与worker pooling性能对比测试.md|L110-L121|train*threads cpu 任务 ego-train batch_size worker gpu 资源 allreduce pdp_vtt_unify_v3_tw
1_6_0 GPU pooling * dense allreduce与worker pooling性能对比测试.md|L122-L123|训练 cpu batch*size gpu c3_v3 c3_v2 g18_v3 速度 置换
1_6_0 GPU pooling * dense allreduce与worker pooling性能对比测试.md|L124-L135|train*threads cpu 任务 ego-train batch_size worker gpu 资源 allreduce pdp_multilabel_vc_search_cate_db_ship_1128_id
1_6_0 GPU pooling * dense allreduce与worker pooling性能对比测试.md|L136-L137|训练 cpu batch*size gpu c3_v3 c3_v2 g18_v3 速度 置换
1_6_0 GPU pooling * dense allreduce与worker pooling性能对比测试.md|L138-L149|deepctr train*threads 模型 cpu 任务 ego-train batch_size worker gpu 资源
1_6_0 GPU pooling * dense allreduce与worker pooling性能对比测试.md|L150-L172|模型 训练 cpu 参数 sparse batch*size 特征 gpu c3_v3 c3_v2
20220117_egotf v0_4.md|L8-L16|day auc p0_click egov0
20220117_egotf v0_4.md|L17-L19|sparse feature number key table counts valid body egov0
20220117_egotf v0_4.md|L20-L21|time cost training egov0 h20m h45m h37m
20220127_egotf v0_4_1.md|L5-L13|day auc p0_click egov0
20220127_egotf v0_4_1.md|L14-L15|sparse feature number key table counts valid body egov0
20220127_egotf v0_4_1.md|L16-L17|time cost training egov0 h20m h45m h37m h30m
20220214_egotf v0_4_2.md|L6-L14|ss day auc p0_click egov0 internal loss func tensorboard trace
20220214_egotf v0_4_2.md|L15-L16|sparse feature ss number key table counts valid body egov0
20220214_egotf v0_4_2.md|L17-L18|ss time cost training egov0 internal loss func tensorboard trace
20220316_egotf v0_4_3.md|L1-L7|sparse ss experiment result dd baseline model dd_fgv7_session_pruning p0_click one
20220316_egotf v0_4_3.md|L8-L10|slot ss experiment result assign-slots model click0
20220316_egotf v0_4_3.md|L11-L14|sparse ss experiment result pdp baseline model sparsednn_pdpv2_multitask_tf_new p0_click one-sparse-input
20220316_egotf v0_4_4.md|L3-L7|sparse experiment result shop baseline model shopv4d2_sppt_sparsednn click
20220316_egotf v0_4_4.md|L8-L9|sparse feature number key table counts valid body egov0
20220316_egotf v0_4_4.md|L10-L11|time cost training egov0 h13m
20220316_egotf v0_4_4.md|L14-L20|sparse experiment result pdp baseline model sparsednn_pdpv2_multitask_tf_nl9 p0_click
20220316_egotf v0_4_4.md|L21-L22|sparse feature number key table counts valid body egov0
20220316_egotf v0_4_4.md|L23-L24|time cost training egov0 h10m h30m
20220606_egotf v0_4_5.md|L3-L9|sparse experiment result pdp baseline model sparsednn_pdpv2_multitask_tf_nl9 click
20220606_egotf v0_4_5.md|L10-L11|sparse feature number key table counts valid body egov0
20220606_egotf v0_4_5.md|L12-L13|time cost training egov0
20220709-egotf 0_4_6 \_not with zmap optimisation and nsc development*.md|L3-L15|slot worker training model dd*feav4_po_fgv2_slotdropout_br experimental config workers cores memory
20220709-egotf 0_4_6 \_not with zmap optimisation and nsc development*.md|L16-L24|sparse worker training model sparsednn*pdpv4_adf_fpv2_d6_sg experimental config workers cores memory
20220709-egotf 0_4_6 \_not with zmap optimisation and nsc development*.md|L27-L41|slot worker checkpoint training model dd*feav4_po_fgv2_slotdropout_br experimental config workers cores
20220714_egotf v0_4_6.md|L3-L11|slot worker training model dd_feav4_po_fgv2_slotdropout_br experimental config workers cores memory
20220714_egotf v0_4_6.md|L12-L20|sparse worker training model sparsednn_pdpv4_adf_fpv2_d6_sg experimental config workers cores memory
2025 NPS survey.md|L1-L2|ps 发布 训练 调优 任务 离线训练 资源 eta yadong soc
A100上worker-ps性能分析.md|L6-L16|train_threads ps 训练 任务 worker a100 xla worker_ps pod max_context
A100上worker-ps性能分析.md|L17-L26|训练 任务 a100 xla aibox pod train threads max context
A100上worker-ps性能分析.md|L27-L29|ps 配置 训练 cpu 显存 半精度 任务 worker gpu 内存
A100上worker-ps性能分析.md|L30-L31|portal ps cpu 任务 worker ego-portal pull push user system
A100上worker-ps性能分析.md|L32-L34|ps 训练 cpu worker 资源 耗时 rpc system time pull
A100上worker-ps性能分析*单机版测试*.md|L4-L6|train_threads 模型 ps 配置 训练 cpu 参数 显存 半精度 任务
A100上worker-ps性能分析*单机版测试*.md|L7-L8|portal ps cpu 任务 worker ego-portal pull push user system
A100上worker-ps性能分析*单机版测试*.md|L9-L11|ps 训练 cpu worker 资源 耗时 rpc system time pull
A30 * L4 性能测试.md|L1-L10|l4 训练 cpu 显存 a30 batch*size gpu dense 内存 allreduce
A30 * L4 性能测试.md|L13-L14|round0 模型 round1 l4 配置 训练 cpu 参数 显存 a30
A30 _ L4 性能测试.md|L15-L16|round0 模型 round1 l4 配置 训练 cpu 参数 显存 a30
A30 _ L4 性能测试.md|L17-L24|监控 l4 显存 a30 带宽 tf32 pdp dsrm 测试 结果
A30 * L4 性能测试.md|L25-L31|模型 ps l4 训练 显存 a30 带宽 ego gb tf32
A30机器网卡带宽测试.md|L1-L4|train_threads 模型 配置 训练 cpu 显存 半精度 任务 worker gpu
A30机器网卡带宽测试.md|L5-L8|train_threads 模型 配置 训练 cpu 显存 半精度 任务 worker gpu
AI-search 改写迁ego.md|L5-L37|模型 ps a30 onnx 部署 gpu 负载均衡 scalar output bf16
AUC Monitor.md|L1-L12|auc monitor detailed metric calculation all metrics below calculated please
AUC Monitor.md|L13-L24|eval ss auc area under curve performance metric often used
AUC Monitor.md|L25-L32|eval ss logloss log loss known logarithmic cross-entropy performance metric
AUC Monitor.md|L33-L38|eval ss rmse root mean squared error commonly used metric
AUC Monitor.md|L39-L44|eval ss mae mean absolute error metric used evaluate performance
AUC Monitor.md|L45-L48|ps ss gauc takes grouped data account meaning averages auc
AUC Monitor.md|L49-L54|ss actualctr actual ctr refers empirical real-world observed rate users
AUC Monitor.md|L55-L60|feature predictedctr predicted ctr refers estimated likelihood probability user click
AUC Monitor.md|L61-L66|calibration predictedctr actualctr provides factor model predicted probabilities usecase overestimation
AUC Monitor.md|L67-L70|totalsamplenum sample_size sum weights all samples
AUC Monitor.md|L71-L74|negativenum negative_sample_size sum weights all samples labels
AUC Monitor.md|L75-L77|positivenum positive_sample_size sum weights all samples labels
AUC monitor introduction.md|L3-L7|portal ego-portal concepts name description counterpart model_name model such din
AUC monitor introduction.md|L8-L21|ss metric panels auc monitor provides training metrics comparison multiple
AUC monitor introduction.md|L22-L27|versioned-level model performance comparison panel row series panels built compare
AUC monitor introduction.md|L28-L33|job-level model performance comparison panel row series panels built compare
AUC monitor introduction.md|L34-L43|ps sorting groups facilitate use view values same metrics group
AUC monitor introduction.md|L44-L83|ps round1 ego-learner ss faq disable auc monitor report function
About Inferencing (Release models to EGO predictor).md|L3-L8|ego-predictor predictor ps publish release workflow ego egocontroller user manual
About Inferencing (Release models to EGO predictor).md|L9-L32|predictor ps slot release dense feature ss prepare config files
About Inferencing (Release models to EGO predictor).md|L33-L95|predictor ps serving release checkpoint model online ego egocontroller user
About Inferencing (Release models to EGO predictor).md|L96-L121|inferencing serving release checkpoint ss one online list finished training
About Inferencing (Release models to EGO predictor).md|L122-L136|release checkpoint period training rule part hope based choose job
About Inferencing (Release models to EGO predictor).md|L137-L150|serving emb release checkpoint mix batch model click new set
About Inferencing (Release models to EGO predictor).md|L151-L190|serving release checkpoint online learning job part there two methods
About Inferencing (Release models to EGO predictor).md|L193-L223|inferencing serving publish checkpoint view batch model list ui trained
About Inferencing (Release models to EGO predictor).md|L224-L252|monitoring ps release ss view online model detail ego egocontroller
About Inferencing (Release models to EGO predictor).md|L253-L267|release config grey choose canary updating proportion pod ip check
About Inferencing (Release models to EGO predictor).md|L270-L275|serving ss view online learning list click model see permission
About Inferencing (Release models to EGO predictor).md|L276-L281|serving ss operate online learning update here resetting sync frequency
About Inferencing (Release models to EGO predictor).md|L282-L325|presstest ss take press test function support own model using
About Inferencing (Release models to EGO predictor).md|L326-L328|ps deploy gr model docs google document yfk4vjygyyvflustkuu3jygholg5cs8mzr9bqaa5dq4 edit usp
About Management.md|L1-L4|project management see tenant level information
About Management.md|L5-L15|ps ss resource dashboard reasonably effectively using training resources important
About Management.md|L16-L24|resource information know tenant choose set project all find these
About Management.md|L25-L28|real time status proportion job requests shown here pie chart
About Management.md|L29-L32|running job usage section see currently data real time default
About Management.md|L33-L36|history job usage section view these metric historical tasks including
About Management.md|L39-L48|serving ss user management ego permission setting consistent soc permissions
About Management.md|L49-L59|resource management current tenant quota usage information project volume task
About Management.md|L60-L63|release project operation record view records click go see ego
About Management.md|L64-L67|ss job count limit setting default ego sets maximum number
About Management.md|L68-L71|ss alert setting set offline webhook online make sure joined
About Management.md|L72-L76|ckpt ps checkpoint hdfs whitelist due current shortage resources ego
About Management.md|L77-L84|ckpt management order better manage users ego set up page
About Management.md|L85-L104|portal ps onlineps ego-portal offlineps management page check status projects
About Management.md|L105-L108|serving ss cost management order measure training inference each version
About Management.md|L109-L116|notebook release cost statement section query usage flow all training
About Management.md|L117-L128|summary bill section view aggregated data according certain dimensions currently
About Management.md|L129-L132|cost analysis section use charts visually compare please click search
About Management.md|L133-L137|portal release notification management latest ego platform supports users see
About Model and Version.md|L5-L16|egotrain create model use ui call create_model sh introduction using
About Model and Version.md|L17-L32|ps feature register model version ego egocontroller user manual register-model-version
About Model and Version.md|L33-L39|ps ss view model list ego egocontroller user manual version
About Model and Version.md|L40-L44|ss delete model no longer only there version under deleted
About Model and Version.md|L45-L51|ps checkpoint ss view model version list ego egocontroller user
About Model and Version.md|L52-L56|ps ss delete model version ego egocontroller user manual delete-model-version
About Model and Version.md|L57-L72|ps publish release checkpoint ss view list ego egocontroller user
About Model and Version.md|L73-L76|ps release checkpoint ss model version permission ego egocontroller user
About Model and Version.md|L77-L91|ps checkpoint hdfs faq why my deleted due shortage resources
About Notebook.md|L13-L20|compile worker print tensor model again rerun solo notice please
About Notebook.md|L21-L27|notebook why open there several common reasons just created may
About Training Job.md|L1-L13|ps offline training job having model corresponding version want execute
About Training Job.md|L14-L40|ps converter ego-learner ss prepare config files ego egocontroller user
About Training Job.md|L41-L120|ps submit batch training job ego egocontroller user manual offline
About Training Job.md|L121-L157|ps view offline training job list ego egocontroller user manual
About Training Job.md|L158-L197|ps checkpoint view training job detail ego egocontroller user manual
About Training Job.md|L198-L218|ps stop training job ego egocontroller user manual offline stop-training-job
About Training Job.md|L219-L241|ps delete training job ego egocontroller user manual offline delete-training-job
About Training Job.md|L242-L245|copy training job ego now supports quick duplication jobs sparing
About Training Job.md|L248-L251|online-learning ps kafka publish checkpoint online learning job introduction ego
About Training Job.md|L252-L259|online-learning ps submit online learning job ego egocontroller user manual
About Training Job.md|L260-L265|ps ss view training job list ego egocontroller user manual
About Training Job.md|L266-L271|online-learning ps checkpoint view online learning job detail ego egocontroller
About Training Job.md|L272-L275|online-learning ps stop online learning job ego egocontroller user manual
About Training Job.md|L276-L279|ps delete copy training job ego egocontroller user manual online
About Training Job.md|L282-L309|ps release period-training checkpoint period training job introduction ego egocontroller
About Training Job.md|L310-L341|ps submit period training job ego egocontroller user manual ui
About Training Job.md|L342-L345|view training job list correspondence between status operation description created
About Training Job.md|L346-L353|release checkpoint view period training job detail see basic information
About Training Job.md|L354-L361|ps period-training hdfs verify start period training job ego egocontroller
About Training Job.md|L362-L365|ps period-training stop period training job ego egocontroller user manual
About Training Job.md|L366-L371|ps inferencing release period-training delete period training job ego egocontroller
About Training Job.md|L372-L382|gpu faq submit training job should choose project want train
Access Process.md|L1-L10|egotrain ss best practices users refer following process access guarantee
Access Process.md|L11-L16|ss permission requests access ego make connection tpm linlan wang
Access Process.md|L19-L24|ss training resources use ego present business needs budget under
Access Process.md|L25-L28|predictor egopredictor ss inference resources currently ego does provide business
Access Process.md|L29-L32|ss model training demo overall access process found following wiki
Access Process.md|L33-L38|code user required provide model definition providing git information used
Access Process.md|L39-L48|ps compile docker image current version users code manually use
Access Process.md|L49-L52|ego_learner converter configuration each training task user needs provide yaml
Access Process.md|L53-L66|egotrain ss hdfs samples currently offers different sample access methods
Access Process.md|L67-L72|deepctr ss types models supported deep learning reinforcement large-scale scenarios
Access Process.md|L73-L78|egotrain predictor egopredictor feature ss online inference overall access process
Access Process.md|L79-L82|feature ss features questions sample generation storage extraction process generator
Access Process.md|L83-L86|portal model training once prepared samples ask jingzhe zhou bill
Access Process.md|L87-L92|predictor publish release egopredictor ss model currently supports storage s3
Access Process.md|L93-L98|ps ss interface invocations suggest use git garena recommend srec_protos
Access Process.md|L99-L105|predictor egopredictor ss naming company doesn unified yet cause brpc
AdaGrad vs DefaultSparse.md|L1-L4|deepctr sparse experiment settings performance difference between adagrad defaultsparse given
AdaGrad vs DefaultSparse.md|L7-L51|ps sparse optimizer parameter defaultsparse shown below lr mf use
AdaGrad vs DefaultSparse.md|L52-L57|sparse ss training curve using adagrad defaultsparse almost same according
AdaGradDecayOptimizer.md|L1-L20|ps emb embedding sparse feature ego adagraddecayoptimizer dim learning_rate initial_accumulator_value
AdaGradOptimizer.md|L1-L18|ps emb embedding sparse feature ego adagradoptimizer dim learning_rate weight_decay
AdaMomOptimizer.md|L1-L19|ps slot emb embedding sparse feature ego adamomoptimizer dim learning_rate
AdamWOptimizer.md|L1-L20|ps emb embedding sparse feature ego adamwoptimizer dim learning_rate weight_decay1
Ads Models Inference Optimization.md|L1-L26|ss optimization pass convert_mul_reducesum_to_matmul rewrite mul-reducesum pattern transepose-matmul- squeeze suppose
Ads Models Inference Optimization.md|L27-L30|deployment each model below modify json add following
Ads Models Inference Optimization.md|L31-L32|eval ps gpu offline gains evaluation model peak qps mode
Appendix.md|L3-L8|ss batch platform distributed computing large-scale processing designed provide easy-to-use
Appendix.md|L9-L13|feature batch platform functions automatic efficient scheduling computations dynamic allocation
Appendix.md|L14-L17|relationship between batch ego training part platform built top services
Appendix.md|L18-L36|egotrain sparse tensorflow most popular deep learning framework industry easy
Appendix.md|L37-L50|egotrain predictor publish egopredictor ss primarily designed take models generated
Appendix.md|L53-L56|portal egoportal provides user api webui all functions ego
Appendix.md|L57-L60|egoscheduler module plays role commander egocontroller managing resources traffic following
Appendix.md|L61-L64|monitoring egosupervisor acts doer egocontroller implementing measures monitor following up
Appendix.md|L65-L70|ps onlineps sparse feature egops parameter server mainly used solve
Appendix.md|L71-L76|egotrain ps feature trainingps work together store model optimize parameters
Appendix.md|L77-L81|predictor ps onlineps egopredictor feature work together store model update
Auc Monitor 数据库优化方案.md|L1-L9|模型 训练 grafana 耗时 版本 egocontroller et_model_metrics_collector_tab model_name m10s auc
Auc Monitor 数据库优化方案.md|L10-L28|模型 任务 worker model_name model_version tenant egocontroller controller 优化 方案
Basic Introduction.md|L1-L16|cpu sparse gpu ego industrial-grade deep learning framework designed optimized
Basic Introduction.md|L21-L33|sparse feature ss adapted larger scale data scenarios ego dedicated
Basic Introduction.md|L34-L44|sparse converter feature ss user friendliness all code available support
BatchNormalization.md|L1-L17|eval ps ego batchnormalization name momentum epsilon e-6 trainable true
Batch交替消费实现方案.md|L7-L14|训练 样本 batch_size data_path sampleshuffle shuffle_window_size tag user_id shuffle batchparser
Benchmark CPU vs GPU*主要是精排模型*.md|L1-L10|emb embedding sparse feature ss concept fs featureservice fg featuregenerator
Benchmark CPU vs GPU*主要是精排模型*.md|L11-L17|deepctr slot emb embedding dense hdfs model c2_v2 numa requestv3
Benchmark CPU vs GPU*主要是精排模型*.md|L18-L23|predictor ps emb cpu result predictv3 no fs fg only
Benchmark CPU vs GPU*主要是精排模型*.md|L26-L33|hdfs items keys- keys r2 user arthur hu uptest dd_fg_fea_v4_click
Benchmark CPU vs GPU*主要是精排模型*.md|L34-L40|items keys- keys client concurrency
Benchmark CPU vs GPU*主要是精排模型*.md|L43-L48|hdfs items r2 user arthur hu uptest dd_fg_fea_v4_click br v1_911
Benchmark CPU vs GPU*主要是精排模型*.md|L49-L54|hdfs items client concurrency r2 user arthur hu uptest dd_fg_fea_v4_click
Benchmark CPU vs GPU*主要是精排模型*.md|L57-L72|predictor ps emb cpu hdfs c2_v2 predictv3 no fs fg
Benchmark CPU vs GPU*主要是精排模型*.md|L73-L85|ps cpu gpu t4 g6_v2 two cards tesla pow gb
Benchmark CPU vs GPU*主要是精排模型*.md|L86-L91|ps cpu gpu ss xla optimize version use directly instead
Benchmark CPU vs GPU*主要是精排模型*.md|L92-L101|ps cpu gpu ss xla optimize version2 use directly instead
Benchmark CPU vs GPU*主要是精排模型*.md|L102-L109|ps cpu a30 gpu g18_v2 two item count qps latency
Benchmark CPU vs GPU*主要是精排模型*.md|L110-L121|ps cpu gpu hdfs din sesion model request files r2
Benchmark CPU vs GPU*主要是精排模型*.md|L122-L262|trt cpu a30 onnx batch_size gpu mini_batch ss search model
Benchmark CPU vs GPU*主要是精排模型*.md|L263-L352|trt a30 gpu g18v3 vs c3v3 rcmd model gpu_dd_feav4_lt_din_ple_unify my
Benchmark CPU vs GPU*主要是精排模型*.md|L353-L368|ps a30 g18v3 vs c3v2 mpi model mfs_din_v3 qps item
Benchmark CPU vs GPU*主要是精排模型*.md|L369-L384|ps trt cpu a30 gpu ss g18v3 vs s1v2 video
Benchmark CPU vs GPU*主要是精排模型*.md|L385-L393|模型 cpu a30 gpu t4 g18v3 dsrm din esmm sim
Benchmark For sse4recall_TF vs* ONNX*.md|L5-L8|benchmark ss tool bin model_stress_test flagfile conf gflags_benchmark benchmark_model_name recforest-zkr-ep
Benchmark For sse4recall_TF vs* ONNX*.md|L19-L26|ps cpu onnx conclusion tensorflow qps qps40 延时 比较 利用率
Benchmark For sse4recall_TF vs* ONNX*.md|L27-L33|ps ss stress test wiht up_client josn request only one
Benchmark for brpc compress.md|L1-L10|predictor egopredictor environment settings test model dd_feav4_longterm_adf_w_cn_onestage vn batch size
Benchmark for brpc compress.md|L11-L13|ps cpu ss test single thread client compress type latency
Benchmark for brpc compress.md|L14-L15|ps cpu ss test max qps compress type concurrency latency
Benchmark of zmap.md|L3-L9|cpu environment settings all program run same machine cores intel
Benchmark of zmap.md|L10-L15|benchmark lock-free single threaded insert figures bellow show time consumption
Benchmark of zmap.md|L16-L19|benchmark lock-free single threaded find existing keys figures bellow show
Benchmark of zmap.md|L20-L23|benchmark lock-free single threaded find nonexistent keys figures bellow show
Benchmark of zmap.md|L24-L27|benchmark erase figures bellow show time consumption all data value
Benchmark of zmap.md|L28-L31|benchmark lock-free multiple threaded find existing keys figures bellow show
Benchmark of zmap.md|L32-L37|emb benchmark locked multiple threaded find existing keys zmap provide
Benchmark of zmap.md|L38-L45|evict benchmark rehash functions provided zmap modified yuan zhong shoppe
Benchmark of zmap.md|L46-L56|conclusion delete operations zmap performance advantage other lock-free operation similar
Benchmark tool.md|L3-L6|portal 模型 发布 benchmark ego 操作 几乎 完全一致 额外 支持
Benchmark tool.md|L7-L10|tensorrt gpu xla tensorflow tf tf-xla direct-xla fp32 tf32 fp16
Benchmark tool.md|L11-L36|predictor presstest 模型 trt 配置 参数 a30 gpu egopredictor ss
Benchmark tool.md|L37-L46|predictor 任务 资源 吞吐 result graph executor tf_run_latency ms throughput
Benchmark tool.md|L47-L50|cpu onnx tf 支持 性能 差异 不大 一般 线上 直接
Benchmark tool.md|L51-L60|配置 cpu 参数 gpu xla machine type c3v2 s1v2 video
Benchmark tool.md|L61-L70|predictor ps cpu release gpu egopredictor local harbor shopeemobile dd
Bisuness enroll.md|L3-L9|predictor mpi promotion liveish ego live-test v1 up predict live
Bisuness enroll.md|L10-L18|predictor opa liveish ego live-test v1 up predict live curl
Bisuness enroll.md|L19-L24|predictor egopredictor security model ready inference tf_df developing
Bisuness enroll.md|L25-L29|feature map search offline model ready mfp developing online context
Business stress test.md|L1-L10|ps cpu gpu t4 mpi promotion mfs_dl_v2 c2v2 json request
Business stress test.md|L11-L26|ps cpu microsite config one machine total per pod item
Business stress test.md|L27-L48|ps cpu bundle config half machine one pod wich item
Business stress test.md|L49-L58|ps cpu mind config half machine one pod wich qps
Business stress test.md|L59-L70|ps cpu mpishop homepage config two pod one machine each
Business stress test.md|L71-L103|predictor hdfs opa request r2 user arthur hu uptest json
Business stress test.md|L104-L117|ps cpu hdfs map search half c3_v2 pod request json
Business stress test.md|L118-L125|ps cpu search sguide config half c3_v2 pod items concurrency
CPU_GPU*非AIBOX**本地多线程共享nn参数方案.md|L1-L12|训练 slot cpu 参数 sparse batch*size gpu ss pod train
CPU_GPU*非AIBOX**本地多线程共享nn参数方案.md|L13-L23|训练 参数 dnncachecontroller nn pull wait*pull_request dnn_data 解决方案 每个 线程
Check failed* feature*config-\_dim\_\_ ** slot_config_dim** \_140 vs 12\_\_ 3001* 65535* 844759398158406894* 2970*0.md|L3-L6|ps 向量 slot emb embedding shared fkey egops 报错 原因
Check failed* gpu*context-\_IsGpuTensor_sparse_data-\_device_data**d_unique_embed_sizes**.md|L3-L7|eval 日志 worker ss i0709 core train pass_batch_queue cc passbatchqueue
Common Functions.md|L1-L4|ss functionality ego platform open business supports user-defined configurations some
Common Functions.md|L5-L20|egotrain predictor ps converter egopredictor ss configurable files supports user-defined
Common Functions.md|L21-L26|user-defined metrics collection support tensorboard specific configuration methods parameters follows
Common Functions.md|L27-L30|user-defined debug tools support users using self-defined
Common Functions.md|L31-L35|portal slot api ego python support individual approaches special pooling
Concept Introduction.md|L1-L6|portal egotrain predictor egopredictor egoportal offers web ui users expected
Concept Introduction.md|L7-L10|model main entity managed ego platform equal concept code experiments
Concept Introduction.md|L11-L14|model version each different versions user upload code training uploaded
Concept Introduction.md|L15-L20|publish ss job unit operation ego platform complete flow operations
Concept Introduction.md|L21-L43|compile training job user creates task series tasks executed sequentially
Concept Introduction.md|L44-L49|publish release checkpoint job once user gets training results they
Concept Introduction.md|L50-L53|task smallest user-visible unit execution within ego system each job
Concept Introduction.md|L54-L59|predictor egopredictor online model refers provide inference capabilities within service
Concept Introduction.md|L62-L65|portal ego api provided egoportal users using protocol
Concept Introduction.md|L66-L69|ego python api provided algorithm researchers using defining models
Concept Introduction.md|L70-L87|ps feature ss access elimination decay use certain policies determine
Concept Introduction.md|L88-L93|slot sparse feature putting all keys together indiscriminately very easy
Concept Introduction.md|L94-L96|round0 ss round user samples organized day hour example there
Config feature admission and evict strategy_deprecated*.md|L3-L7|ps emb embedding sparse feature ss admission only occurs several
Config feature admission and evict strategy*deprecated*.md|L8-L15|ps emb sparse feature partially created ego seen look-up table
Config feature admission and evict strategy*deprecated*.md|L16-L24|evict emb embedding feature completely created ego there score mechanism
Config feature admission and evict strategy*deprecated*.md|L25-L28|evict emb embedding sparse feature ss common those useless rarely
Correctness BenchMarks.md|L3-L6|portal ps cpu ego-portal live-test training job detail nobreadcrumb tab
Correctness BenchMarks.md|L7-L10|portal ps gpu ego-portal live-test training job detail nobreadcrumb tab
Correctness BenchMarks.md|L13-L16|portal ps cpu ego-portal live-test training job detail nobreadcrumb tab
Correctness BenchMarks.md|L17-L20|portal ps gpu ego-portal live-test training job detail nobreadcrumb tab
Correctness BenchMarks.md|L21-L24|portal ps gpu ego-portal xla live-test training job detail nobreadcrumb
Correctness BenchMarks.md|L27-L30|portal ps cpu ego-portal live-test training job detail nobreadcrumb tab
Correctness BenchMarks.md|L31-L33|portal ps gpu ego-portal live-test training job detail nobreadcrumb tab
Correctness BenchMarks* 1_8_2.md|L3-L6|portal ps cpu ego-portal live-test training job detail info tab
Correctness BenchMarks* 1*8_2.md|L7-L10|portal ps gpu ego-portal live-test training job detail info tab
Correctness BenchMarks* 1*8_2.md|L13-L16|portal ps cpu ego-portal live-test training job detail info tab
Correctness BenchMarks* 1*8_2.md|L17-L20|portal ps gpu ego-portal live-test training job detail info tab
Correctness BenchMarks* 1*8_2.md|L23-L34|portal ps cpu worker ego-portal ss live-test training job detail
Correctness BenchMarks* 1*8_2.md|L35-L39|portal ps gpu ego-portal live-test training job detail info tab
Correctness BenchMarks* 1*8_3.md|L3-L6|portal ps cpu ego-portal live-test training job detail info tab
Correctness BenchMarks* 1*8_3.md|L7-L10|portal ps gpu ego-portal live-test training job detail info tab
Correctness BenchMarks* 1*8_3.md|L13-L18|portal ps cpu ego-portal live-test training job detail info tab
Correctness BenchMarks* 1*8_3.md|L19-L22|portal ps gpu ego-portal live-test training job detail info tab
Correctness BenchMarks* 1*8_3.md|L25-L30|portal ps cpu ego-portal live-test training job detail info tab
Correctness BenchMarks* 1*8_3.md|L31-L35|portal ps gpu ego-portal live-test training job detail info tab
Correctness BenchMarks* 1*8_4.md|L3-L8|portal ps cpu ego-portal live-test training job detail info tab
Correctness BenchMarks* 1*8_4.md|L9-L12|portal ps gpu ego-portal live-test training job detail info tab
Correctness BenchMarks* 1*8_4.md|L15-L20|portal ps cpu ego-portal live-test training job detail info tab
Correctness BenchMarks* 1*8_4.md|L21-L24|portal ps gpu ego-portal live-test training job detail info tab
Correctness BenchMarks* 1*8_4.md|L27-L32|portal ps cpu ego-portal live-test training job detail info tab
Correctness BenchMarks* 1*8_4.md|L33-L35|portal ps gpu ego-portal live-test training job detail info tab
Correctness BenchMarks* 1*8_4临时镜像.md|L1-L10|ego-train harbor shopeemobile mlp-ego ego-train-runtime v1 dev-f6f7c305-tf2-sg-20260205031521 dev-f6f7c305-tf2-us-20260205031521 harbo 镜像
Correctness BenchMarks* 1*8_4临时镜像.md|L11-L14|portal deepctr ps ego-portal live-test training job detail info
Correctness BenchMarks* 1*8_4临时镜像.md|L15-L18|portal ps ego-portal din live-test training job detail info
Correctness BenchMarks* 1*8_4临时镜像.md|L19-L22|portal ps sparse ego-portal sparse_adf_dnn live-test training job detail info
Correctness BenchMarks* 1*8_4临时镜像.md|L23-L27|monitoring portal ps grafana ego-train ego-portal cvr_v21_eastasia_place_pay_zjz training job detail
Cpp Converter Optimisation report.md|L20-L38|wc sparse converter dense testing hypothesis debug results sample-converter-printer decreased
Cpp Converter Optimisation report.md|L39-L56|optimizing lua util background does build hash functions writing one
Customise optimisers on each segment of a sparse embedding.md|L1-L11|emb embedding sparse feature ss composed list segments each segment
DNN module.md|L3-L9|config trainable variables different optimisers advantage ego each variable customised
DNN module.md|L10-L15|normalisation ego there two kinds global norm batch forbidden apply
DNN module.md|L16-L18|ps dense ss densetower src contextnavpagetreemode multi-layer class implemented ego
DPDK survey.md|L1-L10|ps benchmark test dpdk seastar follow link github scylladb wiki
DPDK survey.md|L11-L15|ps benchmark system configuration needed support seastar follow link sort
DPDK survey.md|L16-L19|other information dpdk overhead least cores required support effective bandwidth
DR 2025.md|L7-L10|ps 部署 ego dr sg docs google spreadsheets j88ptte8vrl1_pcqx3qzgqhieducyuny_pedjogkpxi edit
DR 2025.md|L13-L20|predictor ps 跨机房 部署 资源 带宽 sg10 psclient zk controller
Data To Disk function \_ego v0_4_7*.md|L3-L15|ego-learner use modify yaml change offline*runner offline_runner_v2 config training data
Data To Disk function \_ego v0_4_7*.md|L18-L27|worker feature hdfs memory optimisations dd*din_longterm_esmm_mpi_ra3_wu data r2 projects rcmd_feature
Data To Disk function \_ego v0_4_7*.md|L28-L31|monitoring ps grafana ego v0 max infra sz ouorwt*nz batch-job-detail
Data To Disk function \_ego v0_4_7*.md|L32-L43|monitoring ps grafana ego latest max infra sz ouorwt*nz batch-job-detail
Data To Disk function \_ego v0_4_7*.md|L44-L47|monitoring ps grafana ego v0 max infra sz ouorwt*nz batch-job-detail
Data To Disk function \_ego v0_4_7*.md|L48-L51|monitoring ps grafana ego latest max infra sz ouorwt*nz batch-job-detail
Data To Disk function \_ego v0_4_7*.md|L52-L54|ps auc performance analysis rcmd breport ego %%++%%++
Declare slots*info and then use it.md|L4-L5|slot ss ego declare_slot_categories slot_ids slot_dims pooling_methods slot_categories none assign_slots
DeepCtr Demo.md|L4-L7|deepctr ps publish prepare configures files training publishing there some
DeepCtr Demo.md|L8-L12|deepctr evict sparse feature ss admission model-design files deepctr_model py
DeepCtr Demo.md|L13-L15|converter ss run files py data processing script ego unable
DeepCtr Demo.md|L18-L20|ps ego-learner configure files training submit job yaml user file
DeepCtr Demo.md|L21-L26|ego-predictor predictor ps slot publish dense feature ss configure files
DeepCtr Demo.md|L35-L38|ps check job status scheduling scripts ego-controller schedulingscriptsinegocontroller-get_job_status sh job_id
DefaultDenseOptimizer.md|L1-L17|ps dense ego defaultdenseoptimizer dim learning_rate ada_decay_rate ada_epsilon e-8 mom_decay_rate
DefaultSparseOptimizer.md|L1-L20|emb embedding sparse feature ego defaultsparseoptimizer dim learning_rate initial_g2sum initial_range
Definitions for target and round \_egotf 0_4_3 and above*.md|L3-L13|ss declare target egotf users should explicitly info ego name
Definitions for target and round _egotf 0_4_3 and above_.md|L14-L27|serving ss round definition egotf there two types offlineround onlineround
DenseTower.md|L5-L23|dense output densetower name output*dims kernel_initializers none bias_initializers activations norms
Doing consistent check with validate samples.md|L1-L5|ego-predictor predictor feature ss using sample info inputs no origin
EGO Common Machine Resources and Conversion Relationships.md|L1-L9|wc predictor ps compile worker offlineps ss ego role descriptions
EGO Common Machine Resources and Conversion Relationships.md|L14-L20|h100 ps cpu a30 worker a100 gpu ss t4 resource
EGO Common Machine Resources and Conversion Relationships.md|L21-L34|h100 cpu a30 worker a100 gpu t4 reference different resource
EGO Common Machine Resources and Conversion Relationships.md|L35-L48|ps cpu gpu ss reference different resource conversions within role
EGO Common Machine Resources and Conversion Relationships.md|L49-L54|l4 inferencing a30 gpu t4 scenario existing cards v100-32 t4other
EGO Common Machine Resources and Conversion Relationships.md|L55-L65|predictor l4 a30 egopredictor t4 resource allocation ratios nodes taking
EGO Common Machine Resources and Conversion Relationships.md|L66-L69|predictor ps onlineps egopredictor resource allocation amount resources cannot simply
EGO Common Machine Resources and Conversion Relationships.md|L70-L79|cpu gpu common machine configurations usage status note memory columns
EGO Controller适配PS2_0.md|L8-L23|ps serving emb embedding controller batch model replica task operation
EGO Controller适配PS2_0.md|L24-L26|ps ego2 psmaster docs google document vvltrwdjvimewn3ejpx6f3ezz-rrtuiuwfutt6ijkcs edit heading lz74tzx7ig79
EGO Core Metrics.md|L5-L46|模型 训练 cpu 参数 样本 sparse 任务 benchmark 稀疏 资源
EGO Core Metrics.md|L47-L59|wc mig 模型 训练 cpu 样本 任务 a30 worker benchmark
EGO Core Metrics.md|L60-L95|portal 模型 ps 配置 训练 emb cpu 任务 a30 gpu
EGO Core Metrics.md|L96-L101|ckpt predictor ps 任务 benchmark inference git garena ego predictor-tools
EGO Core Metrics.md|L102-L107|模型 cpu 参数 benchmark 稀疏 checkpoint plan size keys nn
EGO Core Metrics.md|L108-L111|模型 参数 稀疏 gpu checkpoint size keys nn requests path
EGO Core Metrics.md|L116-L117|模型 训练 cpu 任务 gpu 资源 job train image version
EGO Core Metrics.md|L118-L119|predictor 模型 ps 推理 版本 request qps x2 latency p90
EGO Core Metrics.md|L120-L122|monitoring ps 训练 推理 grafana ego-train worker benchmark 资源 ss
EGO Core Metrics.md|L123-L128|模型 训练 同步 emb cpu kafka 参数 推理 样本 sparse
EGO Core Metrics.md|L129-L144|配置 训练 任务 hdfs sli training fail rate sandbox online-export
EGO Core Metrics.md|L145-L157|monitoring 模型 ps 监控 grafana model version link infra sz
EGO FAQ Manual.md|L7-L25|predictor 模型 ps slot sparse 任务 日志 question example sandbox
EGO NPS survey.md|L1-L6|ps reports docs google document lnijv6swa1jtq_iww1bsienrgmcvvmejx4nnzbymrc edit usp sharing presentation
EGO NPS survey.md|L7-L10|ego 结论 相比 上一年 今年 平台 赢得 推荐者 用户 被动
EGO NPS survey.md|L11-L14|notebook 版本 todo lists model eta terminal git q1 q2
EGO Online Model Operation Log Record on Shopee Eagle Eye.md|L1-L4|monitoring feature overview ego supports efficiently managing deep learning model
EGO Online Model Operation Log Record on Shopee Eagle Eye.md|L5-L9|ss operation types following table describes currently supported online model
EGO Online Model Operation Log Record on Shopee Eagle Eye.md|L10-L13|log format each operation reported eagle eye contains detailed information
EGO Online Model Operation Log Record on Shopee Eagle Eye.md|L14-L27|basic information event title descriptive indicating operation type related model
EGO Online Model Operation Log Record on Shopee Eagle Eye.md|L28-L34|checkpoint tags online_model_id unique online model being operated ego online_model_version_id
EGO Online Model Operation Log Record on Shopee Eagle Eye.md|L35-L42|ps release query see web ui space reliability event_centre end_date
EGO Online Model Operation Log Record on Shopee Eagle Eye.md|L43-L49|feedback contact information any new requirements suggestions bug reports please
EGO PS CLI USER GUIDE.md|L7-L20|ps ss method online service access directly through browser soc
EGO PS CLI USER GUIDE.md|L21-L46|ego-train 版本 method local installation start any version docker container
EGO PS CLI USER GUIDE.md|L47-L62|starting cli run tool enter interactive command line interface note
EGO PS CLI USER GUIDE.md|L63-L68|common function guide entering cli interface execute help see available
EGO PS CLI USER GUIDE.md|L69-L74|env management sg show status 环境 管理 切换 工作 查看
EGO PS CLI USER GUIDE.md|L75-L84|ps onlineps cluster management show clusters describe onlineps-common_sg10 replicas use
EGO PS CLI USER GUIDE.md|L85-L98|模型 配置 sparse gpu model management show models filter prerank
EGO PS CLI USER GUIDE.md|L99-L123|starting get error version glibcxx_3 xx found please ensure libstdc
EGO Portal User Manual.md|L1-L6|model version ego follow following design starting training task determine
EGO Portal User Manual.md|L7-L41|egotrain register model use ego-controller ui create call create_model sh
EGO Portal User Manual.md|L42-L87|ps register model version ego egocontroller user manual register-model-version mentioned
EGO Portal User Manual.md|L88-L115|ps view model list ego egocontroller user manual version view-model-list
EGO Portal User Manual.md|L116-L137|ps ss delete model ui ego egocontroller user manual version
EGO Portal User Manual.md|L138-L165|ps ss view model version list ego egocontroller user manual
EGO Portal User Manual.md|L166-L188|ps ss delete model version ego egocontroller user manual delete-model-version
EGO Portal User Manual.md|L189-L217|ckpt ps publish release checkpoint ss view list ego egocontroller
EGO Portal User Manual.md|L218-L222|ckpt ps release ss model version permission ego egocontroller user
EGO Portal User Manual.md|L225-L237|ps offline training job having model corresponding version want execute
EGO Portal User Manual.md|L238-L264|ps converter ego-learner ss prepare config files ego egocontroller user
EGO Portal User Manual.md|L265-L325|ps submit batch training job ego egocontroller user manual offline
EGO Portal User Manual.md|L326-L362|ps view offline training job list ego egocontroller user manual
EGO Portal User Manual.md|L363-L402|ps checkpoint view training job detail ego egocontroller user manual
EGO Portal User Manual.md|L403-L423|ps stop training job ego egocontroller user manual offline stop-training-job
EGO Portal User Manual.md|L424-L446|ps delete training job ego egocontroller user manual offline delete-training-job
EGO Portal User Manual.md|L447-L450|copy training job ego now supports quick duplication jobs sparing
EGO Portal User Manual.md|L453-L456|online-learning ps kafka publish checkpoint online learning job introduction ego
EGO Portal User Manual.md|L457-L464|online-learning ps submit online learning job ego egocontroller user manual
EGO Portal User Manual.md|L465-L470|ps ss view training job list ego egocontroller user manual
EGO Portal User Manual.md|L471-L476|online-learning ps checkpoint view online learning job detail ego egocontroller
EGO Portal User Manual.md|L477-L480|online-learning ps stop online learning job ego egocontroller user manual
EGO Portal User Manual.md|L481-L484|ps delete copy training job ego egocontroller user manual online
EGO Portal User Manual.md|L487-L514|ps release period-training checkpoint period training job introduction ego egocontroller
EGO Portal User Manual.md|L515-L546|ps submit period training job ego egocontroller user manual ui
EGO Portal User Manual.md|L547-L550|view training job list correspondence between status operation description created
EGO Portal User Manual.md|L551-L558|release checkpoint view period training job detail see basic information
EGO Portal User Manual.md|L559-L566|ps period-training hdfs verify start period training job ego egocontroller
EGO Portal User Manual.md|L567-L570|ps period-training stop period training job ego egocontroller user manual
EGO Portal User Manual.md|L571-L576|ps inferencing release period-training delete period training job ego egocontroller
EGO Portal User Manual.md|L579-L582|ego-predictor predictor release models ego finishing offline training users online
EGO Portal User Manual.md|L583-L588|ego-predictor predictor ps publish release workflow ego egocontroller user manual
EGO Portal User Manual.md|L589-L612|predictor ps slot release dense feature ss prepare config files
EGO Portal User Manual.md|L613-L769|predictor ps serving release checkpoint model online ego egocontroller user
EGO Portal User Manual.md|L772-L803|inferencing serving publish checkpoint view batch model list ui trained
EGO Portal User Manual.md|L804-L832|monitoring ps release ss view online model detail ego egocontroller
EGO Portal User Manual.md|L833-L847|release config grey choose canary updating proportion pod ip check
EGO Portal User Manual.md|L850-L855|serving ss view online learning list click model see permission
EGO Portal User Manual.md|L856-L861|serving ss operate online learning update here resetting sync frequency
EGO Portal User Manual.md|L862-L903|presstest ss take press test function support own model using
EGO Portal User Manual.md|L904-L907|project management see tenant level information
EGO Portal User Manual.md|L908-L917|resource information know tenant choose set project all find these
EGO Portal User Manual.md|L918-L921|ss user management resource now ego manages permission setting through
EGO Portal User Manual.md|L922-L925|ss job count limit setting default ego sets maximum number
EGO Portal User Manual.md|L926-L929|ss alert setting set offline webhook online make sure joined
EGO Portal User Manual.md|L930-L933|ckpt ps checkpoint hdfs archived setting due current shortage resources
EGO Portal V0.4.0 PRD.md|L1-L8|notebook changes dashboard- status 修改 重新 显示 过滤 数目 设计
EGO Portal V0.4.0 PRD.md|L11-L16|notebook 训练 资源 products involved ol 看板 其他 需求
EGO Portal V0.4.0 PRD.md|L17-L76|notebook 上线 ss progress fe exmple complete incomplete resource management
EGO Portal V0.4.0 PRD.md|L81-L94|cpu 任务 gpu 资源 page frame project management tab remain
EGO Portal V0.4.0 PRD.md|L95-L118|gpu 资源 resource dashboard slice top10 job others name hover
EGO Portal V0.4.0 PRD.md|L119-L159|模型 发布 配置 notebook 训练 资源 版本 ego git version
EGO Portal V0.4.0 PRD.md|L160-L185|notebook feature model management copy version edit no sub-feature ui
EGO Portal V0.4.0 PRD.md|L186-L193|notebook 资源 model list project tab personal all name status
EGO Portal V0.4.0 PRD.md|L194-L250|任务 告警 worker ss online learning hpa lag min count
EGO Portal V0.4.0 PRD.md|L251-L274|ckpt ps 配置 feature train job load nn page management
EGO Portal V0.4.0 PRD.md|L275-L313|portal ckpt 模型 配置 serving release desc basic info edit
EGO Portal V0.4.0 PRD.md|L314-L319|ckpt 发布 训练 任务 release 资源 gnn ego figma production
EGO Portal V0.4.0 PRD.md|L320-L331|ckpt ps serving 同步 others bug greedy load mode button
EGO Portal V0.4.1 PRD.md|L1-L2|prd release ss status issues remark requirement gathering done product
EGO Portal V0.4.1 PRD.md|L7-L10|训练 checkpoint sync sg us 支持 用户 产生 传输 反之
EGO Portal V0.4.1 PRD.md|L21-L26|ckpt changes controller api ui 删除 文明 工具 相关 功能
EGO Portal V0.4.1 PRD.md|L33-L54|上线 checkpoint ss progress fe exmple complete incomplete sync sg
EGO Portal V0.4.1 PRD.md|L59-L91|同步 checkpoint page frame model version operation sync management sg
EGO Portal V0.4.1 PRD.md|L92-L117|发布 配置 训练 checkpoint sync use flow ego quick validation
EGO Portal V0.4.1 PRD.md|L118-L132|ckpt ps checkpoint others load import parameters please refer here
EGO Portal V0.4.2 PRD.md|L3-L5|prd release ss status issues remark requirement gathering done product
EGO Portal V0.4.2 PRD.md|L6-L46|发布 notification management ui ux lists page tab ego live
EGO Portal V0.4.3 PRD.md|L1-L3|prd release ss status issues remark requirement gathering done product
EGO Portal V0.4.3 PRD.md|L6-L13|ckpt 配置 训练 任务 hdfs 版本 requirements list fe training
EGO Portal V0.4.3 PRD.md|L14-L18|训练 expected roi online learning ads ego 支持 推荐 安全
EGO Portal V0.4.3 PRD.md|L23-L26|portal ps l4 ego-portal prototype link figma file pv2h9ztffis4sj0q7sfhzs ego-portal4
EGO Portal V0.4.3 PRD.md|L27-L32|serving release products involved training offline period online learning page
EGO Portal V0.4.3 PRD.md|L35-L62|配置 训练 任务 marker offline training additional support di update
EGO Portal V0.4.3 PRD.md|L63-L67|模型 发布 ol model_date model_timestamp validation files update script demo
EGO Portal V0.4.4 PRD.md|L1-L3|prd release ss status issues remark requirement gathering done product
EGO Portal V0.4.4 PRD.md|L10-L13|训练 资源 expected roi sg 提升 搜推 集群 特别 直播
EGO Portal V0.4.4 PRD.md|L18-L24|任务 feature 版本 prototype resource dashboard history job usage lists
EGO Portal V0.5.0 PRD.md|L1-L14|portal ckpt ps 资源 changes changed batch soc ego job
EGO Portal V0.5.0 PRD.md|L17-L25|presstest ps serving ss products involved management cost notification batch
EGO Portal V0.5.0 PRD.md|L26-L133|ps 上线 ss progress fe exmple complete incomplete project management
EGO Portal V0.5.0 PRD.md|L136-L143|ps management replica 修改 增加 集群 粒度 信息 状态 对应
EGO Portal V0.5.0 PRD.md|L144-L153|ps frame design dashboard tab management tenant operation landing 本期
EGO Portal V0.5.0 PRD.md|L154-L171|ps 监控 dashboard user flow tenant online offline cluster information
EGO Portal V0.5.0 PRD.md|L172-L181|ps 延迟 cost management docs google document blfvrlnmps8yarntw4e6hrygg9-4_8oz7zghx1gyjw edit usp
EGO Portal V0.5.0 PRD.md|L182-L223|发布 notification management moved ui ux lists page tab ego
EGO Portal V0.5.0 PRD.md|L224-L242|presstest ps 配置 tensorrt 任务 minibatch ss xla qps latency
EGO Portal V0.5.1 PRD.md|L5-L40|portal requirements list p0 p1 p3 支持 压缩包 文件 查看
EGO Portal V0.5.1 PRD.md|L45-L50|serving model job zip 创建 页面 更新 详情 改动 涉及
EGO Portal V0.5.1 PRD.md|L51-L56|serving model job code viewer 创建 页面 更新 详情 增加
EGO Portal V0.5.1 PRD.md|L57-L76|发布 serving 同步 参数 release period train rule tab section
EGO Portal V0.5.1 PRD.md|L77-L109|presstest ps 配置 serving tensorrt 任务 minibatch ss xla qps
EGO Portal V0.5.1.1 PRD.md|L3-L12|serving 任务 compile require lists url online model batch detail
EGO Portal V0.5.1.1 PRD.md|L13-L41|serving 任务 compile requirements detail url online model batch config
EGO Portal V0.5.2 PRD.md|L19-L20|ckpt serving 任务 compile requirements list support ue load ckptrollback
EGO Portal V0.5.2 PRD.md|L23-L28|slot emb 参数 feature ss ue fill field slots hit
EGO Portal V0.5.2 PRD.md|L29-L60|ckpt 模型 ps cpkt docs google document rfc4gr1hyp3wjzbwujk_8wttpjiaqf7pdsh_6laetg edit heading
EGO Portal V0.5.2 PRD.md|L61-L64|ckpt 训练 参数 资源 load train 尝试 优化 导入 外部
EGO Portal V0.5.2 PRD.md|L67-L71|serving 任务 日志 owner admin project 增加 周期性 操作 变更
EGO Portal V0.5.2 PRD.md|L72-L74|pending time limit minutes hours seconds days 支持 多种 粒度
EGO Portal V0.5.3 PRD.md|L5-L14|release 资源 objectives significance ego lite 优化 用户 体验 使用率
EGO Portal V0.5.3 PRD.md|L25-L26|ckpt ps 告警 offlineps hdfs requirements list online export load
EGO Portal V0.5.3 PRD.md|L31-L34|py zip 需求 目的 当前 支持 对比 希望
EGO Portal V0.5.3 PRD.md|L35-L52|版本 py zip diff zip1-zip2 v1 aa bb cc ee
EGO Portal V0.5.3 PRD.md|L53-L66|version detail files ending py zip compared diff 需求 设计
EGO Portal V0.5.3 PRD.md|L67-L78|ckpt ps 训练 任务 offlineps online export load batch validation
EGO Portal V0.5.3 PRD.md|L81-L87|monitoring ps 监控 配置 ego-lite grafana 任务 ego lite train
EGO Portal V0.5.4 PRD.md|L5-L14|notebook 告警 objectives significance tb git model predicotr 确保 正常
EGO Portal V0.5.4 PRD.md|L23-L26|portal ps prototype link figma design znqnl2n31awol5mefjgcda portal1 node-id binycc9qibldxoyx-1
EGO Portal V0.5.4 PRD.md|L29-L32|wc ps notebook 训练 任务 requirements list docs google spreadsheets
EGO Portal V0.5.4 PRD.md|L39-L59|notebook feature soc job status tag model version running stop
EGO Portal V0.5.4 PRD.md|L60-L73|portal 白名单 配置 训练 任务 资源 v1 offline training period
EGO Portal V0.5.4 PRD.md|L74-L101|模型 发布 配置 训练 任务 feature git model part1 version
EGO Portal V0.5.4 PRD.md|L104-L109|ps layout homepage docs google document ngzitkoanicg7-exkg3wbek4xvdszc2szbduatgee74 edit 需求 目的
EGO Portal V0.5.4 PRD.md|L110-L131|feature hover icon user guide unleash power ego explore all
EGO Portal V0.5.4 PRD.md|L136-L143|deepctr ps tips model json online-export link pages viewpage action
EGO Portal V0.5.4 PRD.md|L144-L156|ckpt presstest 配置 serving 任务 ss copy period training batch
EGO Portal V0.5.4 PRD.md|L157-L161|配置 batch size number instance one 压测 优化 名称 更正
EGO Portal V0.6.0 PRD.md|L5-L14|predictor 模型 配置 训练 objectives significance bit ipredictor2 支持 脉络
EGO Portal V0.6.0 PRD.md|L23-L26|portal ps prototype link figma design znqnl2n31awol5mefjgcda portal1 node-id binycc9qibldxoyx-1
EGO Portal V0.6.0 PRD.md|L29-L32|wc predictor ps serving requirements list docs google spreadsheets kzbvbjejjrc5w1dxikiwc-lt3mmmwwj64tyxjoamlyw
EGO Portal V0.6.0 PRD.md|L35-L65|白名单 ps 配置 训练 半精度 任务 离线训练 bits perf docs
EGO Portal V0.6.0 PRD.md|L66-L96|predictor serving 推理 部署 predictor2 ego project zk s3 pod
EGO Portal V0.6.0 PRD.md|L97-L102|compile release offline training task job online export sample dat
EGO Portal V0.6.0 PRD.md|L103-L108|模型 ps link docs google document qfkgyo09whvfutcudqiestmviyz0kvdn_ktoegtlpz0 edit heading heat3b25r0dt
EGO Portal V0.6.0 PRD.md|L109-L114|模型 serving 训练 推理 任务 model model-version serving-version 需求 目的
EGO Portal V0.6.0 PRD.md|L115-L119|模型 serving model version tab 需求 概括 增加 信息 尽可能
EGO Portal V0.6.0 PRD.md|L120-L126|ckpt serving version job 依赖 项以 方式 保留 展示 脉络
EGO Portal V0.6.0 PRD.md|L127-L129|ckpt serving feature prototype model basic info version lists tab
EGO Portal V0.6.0 PRD.md|L134-L143|ps 配置 训练 任务 资源 train docs google document ebrcqqyk9_ldo6ojys2aihruwaeotihndzqgxhuz_i
EGO Portal V0.6.0 PRD.md|L144-L151|配置 cpu 任务 gpu 资源 mem 支持 展示 所设 总和
EGO Portal V0.6.0 PRD.md|L152-L155|训练 sandbox batch 支持 跳过 普通 时间 更快
EGO Portal V0.6.0 PRD.md|L156-L163|配置 serving 同步 days hours minutes seconds pending time limit
EGO Portal V0.6.0 PRD.md|L168-L179|ps priority training task filled integer between default lowest highest
EGO Portal V0.6.0 PRD.md|L180-L183|ckpt eval 参数 load train type 支持 导入 外部 二选
EGO Portal V0.6.0 PRD.md|L186-L191|fix batch size number instance one 压测 相关 功能 名称
EGO Portal V0.6.0 PRD.md|L196-L198|git repo-- 进一步 支持 上传 深入 具体 目录 一级 二级
EGO Portal V0.6.0.1 PRD.md|L1-L12|ps 训练 cpu gpu sg my docs google spreadsheets kbuircqignuboiphevag1ujcv4obzhuwiewoqq4ozwq
EGO Portal V0.6.0.1 PRD.md|L13-L14|模型 配置 cpu 任务 gpu 资源 p0 zonep0 p1 ego
EGO Portal V0.6.0.1 PRD.md|L15-L16|模型 job offline training period 功能 设计方案 判断 是否 为线
EGO Portal V0.6.1.1 PRD.md|L1-L4|上线 int8 uat live 背景 根据 实验 过程 发现 问题
EGO Portal V0.6.1.1 PRD.md|L5-L11|ps 配置 feature lists no screen shot offline training period
EGO Portal V0.6.2 PRD.md|L1-L28|ckpt predictor eval 训练 emb embedding ads user ego load
EGO Portal V0.6.2 PRD.md|L29-L32|portal ps figma design znqnl2n31awol5mefjgcda portal1 node-id k0b6zm3nb3lyy3nf-0 功能设计
EGO Portal V0.6.2 PRD.md|L33-L38|ckpt 配置 训练 任务 feature load incremental training default full
EGO Portal V0.6.3 PRD.md|L5-L8|portal ps figma design znqnl2n31awol5mefjgcda portal1 node-id k0b6zm3nb3lyy3nf-0 功能设计
EGO Portal V0.6.3 PRD.md|L9-L15|serving release job link name 修改 跳转 页面 当前 发送
EGO Portal V0.6.3 PRD.md|L16-L21|配置 训练 任务 上线 release admin changelog project period training
EGO Portal V0.6.3 PRD.md|L22-L25|release delete rule period 增加 提醒 确认 对于 删除
EGO Portal V0.6.3 PRD.md|L26-L29|cost management fix all 按钮 当前 排版 错乱 情况 搜索
EGO Portal V0.6.3 PRD.md|L30-L45|ckpt 模型 发布 配置 serving release 版本 version name history
EGO Portal V0.6.3 PRD.md|L46-L69|配置 serving 训练 同步 emb release admin period train owner
EGO Portal V0.6.3 PRD.md|L70-L73|模型 发布 训练 部署 资源 zone us 支持 多个 服务
EGO Portal V0.6.3 PRD.md|L78-L99|ckpt serving emb 上线 project member admin todo 支持 手动
EGO Portal V0.6.3.1 PRD.md|L1-L4|predictor 版本 management 背景 根据 用户 反馈 再次 优化
EGO Portal V0.6.3.1 PRD.md|L5-L8|portal ps figma design znqnl2n31awol5mefjgcda portal1 node-id k0b6zm3nb3lyy3nf-0 功能设计
EGO Portal V0.6.3.1 PRD.md|L9-L15|serving release job link name 修改 跳转 页面 当前 发送
EGO Portal V0.6.3.1 PRD.md|L16-L21|配置 训练 任务 上线 release admin changelog project period training
EGO Portal V0.6.3.1 PRD.md|L22-L25|release delete rule period 增加 提醒 确认 对于 删除
EGO Portal V0.6.3.1 PRD.md|L26-L29|cost management fix all 按钮 当前 排版 错乱 情况 搜索
EGO Portal V0.6.3.1 PRD.md|L30-L45|ckpt 模型 发布 配置 serving release 版本 version name history
EGO Portal V0.6.3.1 PRD.md|L46-L69|配置 serving 训练 同步 emb release admin period train owner
EGO Portal V0.6.3.1 PRD.md|L70-L73|模型 发布 训练 部署 资源 zone us 支持 多个 服务
EGO Portal V0.6.3.1 PRD.md|L78-L85|serving emb project member admin 支持 手动 加白 即使 流量
EGO Portal V0.7.0 PRD.md|L1-L2|prd release ss status issues remark requirement gathering done product
EGO Portal V0.7.0 PRD.md|L17-L20|portal ps prototype link figma design znqnl2n31awol5mefjgcda portal1 node-id binycc9qibldxoyx-1
EGO Portal V0.7.0 PRD.md|L23-L25|模型 发布 serving 告警 release 资源 requirements list banner sandbox
EGO Portal V0.7.0 PRD.md|L28-L42|资源 project soc ego 背景 当前 下面 功能 包括 多个
EGO Portal V0.7.0 PRD.md|L43-L57|feature ss tab project all permission limitation white lists alert
EGO Portal V0.7.0 PRD.md|L58-L95|portal predictor ps 监控 训练 推理 资源 project resource tenant
EGO Portal V0.7.0 PRD.md|L100-L109|ckpt 发布 配置 serving release api period train rule online
EGO Portal V0.7.0 PRD.md|L114-L117|ckpt 模型 发布 update failed 逻辑 优化 对齐 支持 一键
EGO Portal V0.7.0 PRD.md|L118-L123|发布 serving release online learning fp16 period api 逻辑 优化
EGO Portal V0.7.0 PRD.md|L128-L135|monitoring predictor 模型 ps cpu gpu traffic here refers whether
EGO Portal V0.7.0 PRD.md|L140-L151|portal ckpt ps serving release ego-portal job detail training basic
EGO Portal V0.7.5 PRD.md|L1-L46|ps 训练 ol period train docs google document p5xls4pbaqp5l6drbq4dhbmm6s3wlrviqkrkqlidoqg edit
EGO Portal V0.7.5 PRD.md|L47-L63|ckpt predictor 模型 ps 发布 训练 延迟 release 资源 版本
EGO Portal V0.7.5 PRD.md|L64-L75|任务 ss graph only task presst test perf_type 支持 模式
EGO Portal V0.7.5 PRD.md|L76-L87|serving 参数 release batch model update customized gray turn switch
EGO Portal V0.7.6 PRD.md|L1-L13|ps serving 参数 nn online learning basic information update acceleration
EGO Portal V0.8.0 PRD.md|L3-L5|ckpt predictor 模型 告警 requirements list ego project online learning
EGO Portal V0.8.0 PRD.md|L6-L27|portal ps ego docs google document xuzc6atad7wjnvojf6ngd4tbzzhlygfxcjljrsgar-e edit usp sharing
EGO Portal V0.8.0 PRD.md|L28-L69|ckpt 白名单 owner operator operation time name hover landing page
EGO Portal V0.8.0 PRD.md|L70-L80|prd ps online learning sop nn export fix docs google
EGO Portal V0.8.0 PRD.md|L81-L86|predictor 配置 management soc 优化 修改 服务 更新 不对 状态
EGO Portal V0.8.0 PRD.md|L87-L130|ckpt 模型 ps 配置 serving 训练 ego learner name retry
EGO Portal V0.8.0 PRD.md|L131-L138|serving 训练 任务 period rule 支持 在线 修改 文件 创建
EGO Portal V0.8.1 PRD.md|L5-L10|ps ubt dataset datasuite dashboard d68eb-245f-4192-89d4-d08a22801e04 normal no column desc
EGO Portal V0.8.1 PRD.md|L11-L49|portal ps datasuite dashboard e5ecc01c-aacb-473b-a7a9-d2b2490522c3 normal page basic metric distinct
EGO Portal V0.8.2 PRD-智能机器人项目调研与demo设计.md|L5-L7|日志 faq dod link 场景 举例 文档 用户 知道 关于
EGO Portal V0.8.2 PRD-智能机器人项目调研与demo设计.md|L8-L14|任务 demo ego dod seatalk v1 第二 部分 流程 说明
EGO Portal V0.8.2 PRD-智能机器人项目调研与demo设计.md|L17-L30|ps ss di diana aspect details datasuite documentations menu_id menu_1726036575721_1
EGO Portal V0.8.2 PRD-智能机器人项目调研与demo设计.md|L31-L32|ss diana intelligent advisor apple support assistant 竞品 参考价值 打分
EGO Portal V0.8.2 PRD-智能机器人项目调研与demo设计.md|L33-L34|配置 任务 diana prompt 智能 问答 机器人 功能 细项 能力
EGO Portal V0.8.2 PRD-智能机器人项目调研与demo设计.md|L35-L57|ps ss compass assistant llm assistants seatalk ai bot platform
EGO Portal V0.9.0 PRD(备份）.md|L3-L5|kafka release checkpoint requirements list online learning consumption time setting
EGO Portal V0.9.0 PRD(备份）.md|L6-L27|portal ps ego docs google document xuzc6atad7wjnvojf6ngd4tbzzhlygfxcjljrsgar-e edit usp sharing
EGO Portal V0.9.0 PRD(备份）.md|L28-L51|ckpt 白名单 发布 huatuo time name hover landing page bot
EGO Portal V0.9.0 PRD(备份）.md|L52-L57|模型 发布 serving release 版本 batch model rule group name
EGO Portal V0.9.0 PRD(备份）.md|L58-L67|配置 同步 cpu 资源 vq offline batch train gnn mem
EGO Portal V0.9.0 PRD(备份）.md|L68-L71|配置 训练 ego learner 支持 周期性 自定义 跳过 大促 数据
EGO Portal V0.9.0 PRD(备份）.md|L72-L79|ckpt serving name 流量 情况 显示 详情页 增加 时间 取出
EGO Portal V0.9.0 PRD(备份）.md|L82-L97|模型 offline model still traffic last hour sure want take
EGO Portal V0.9.0 PRD(备份）.md|L98-L105|serving 训练 任务 period rule 支持 在线 修改 文件 创建
EGO Portal V0.9.0 PRD(备份）.md|L108-L111|训练 job latest status rule 周期性 列表 增加 一列 显示
EGO Portal V0.9.0 PRD(备份）.md|L112-L115|ckpt 训练 任务 dump only latest sample off 周期性 支持
EGO Portal V0.9.0 PRD(备份）.md|L116-L118|ckpt checkpoint name personal lists trashcan tab 垃圾桶 支持 按照
EGO Portal V0.9.0 PRD.md|L1-L10|资源 changes workspace review 按照 第二轮 评审 意见 修改 细节
EGO Portal V0.9.0 PRD.md|L11-L13|ckpt 模型 serving 训练 告警 资源 requirements list ego project
EGO Portal V0.9.0 PRD.md|L14-L49|prd predictor 模型 ps 训练 任务 资源 ego review workspace
EGO Portal V0.9.0 PRD.md|L50-L71|prd 模型 参数 资源 huatuo review details job 支持 项目
EGO Portal V0.9.0 PRD.md|L72-L77|模型 发布 serving release 版本 batch model rule group name
EGO Portal V0.9.0 PRD.md|L78-L87|配置 同步 cpu 资源 vq offline batch train gnn mem
EGO Portal V0.9.0 PRD.md|L88-L91|配置 训练 ego learner 支持 周期性 自定义 跳过 大促 数据
EGO Portal V0.9.0 PRD.md|L92-L99|ckpt serving name 流量 情况 显示 详情页 增加 时间 取出
EGO Portal V0.9.0 PRD.md|L102-L117|模型 offline model still traffic last hour sure want take
EGO Portal V0.9.0 PRD.md|L118-L125|serving 训练 任务 period rule 支持 在线 修改 文件 创建
EGO Portal V0.9.0 PRD.md|L128-L131|训练 job latest status rule 周期性 列表 增加 一列 显示
EGO Portal V0.9.0 PRD.md|L132-L135|ckpt 训练 任务 dump only final batch off 周期性 支持
EGO Portal V0.9.0 PRD.md|L136-L139|ckpt checkpoint name personal lists trashcan tab 垃圾桶 支持 按照
EGO Portal V0.9.0 PRD.md|L140-L147|portal ckpt ps ego-portal checkpoint ss reshuffle api live sg
EGO Portal V0.9.0 PRD.md|L148-L161|predictor ps 监控 资源 feature v2 tab offline resource vs
EGO Portal V0.9.0 PRD.md|L162-L185|模型 switch name auto offload no traffic reminder text system
EGO Portal V0.9.1 PRD.md|L1-L18|portal ps 调优 任务 资源 ego running jobs usage history
EGO Portal V0.9.1 PRD.md|L21-L40|portal ps ego project related cluster name bind more unbind
EGO Portal V0.9.1 PRD.md|L41-L52|portal ps ego-portal management resourcemanagement list historytab lists jobtab job
EGO Portal V0.9.1 PRD.md|L53-L121|ps l4 调优 docs google document rimc9bypltql4ggiu3hmxqiz5hn1o_lb_oy8oefn-dy edit tab running
EGO Portal V1.0.0 PRD （draft）.md|L5-L10|ps objectives significance support controller big new change docs google
EGO Portal V1.0.0 PRD （draft）.md|L19-L20|requirements list 序号 需求
EGO Portal V1.0.0 PRD （draft）.md|L31-L34|ckpt 训练 参数 资源 load train 尝试 优化 导入 外部
EGO Portal V1.0.0 PRD （draft）.md|L37-L40|任务 日志 project 增加 周期性 操作 变更 恢复 权限 支持
EGO SLA_QoS_HA.md|L1-L12|egotrain ps design architecture whole ego system docs google document
EGO SLA_QoS_HA.md|L13-L15|portal predictor ps 监控 训练 告警 限流 standard sla qos
EGO SLA_QoS_HA.md|L16-L59|监控 训练 任务 日志 上线 资源 ss hdfs measures offline
EGO Team Introduction.md|L3-L6|arthur hu email comlocations bj-qidi-f26-b-p-6 self introduction joined worked avic-it
EGO Team Introduction.md|L7-L9|baolong guo resigned email comlocations sg self introduction joined worked
EGO Team Introduction.md|L10-L13|bill wu email comlocations bj-qidi-f26-b-p-1 self introduction joined worked kuaishou
EGO Team Introduction.md|L14-L15|emb dang truong email comlocation sg spd office self introduction
EGO Team Introduction.md|L16-L17|ss feichao ma email comlocations bj-f26-b-p-4 self introduction joined may
EGO Team Introduction.md|L18-L19|fulong tan resigned email comlocations sg self introduction joined software
EGO Team Introduction.md|L20-L21|ps huaidong gao email comlocations cndc self introduction fudan universiy2020
EGO Team Introduction.md|L22-L23|jian yang email comlocations bj-f26-b-o-4 self introduction graduated bachelor master
EGO Team Introduction.md|L24-L25|jinghao feng transferred email comlocations sg-5f-aa6 self introduction graduated bachelor
EGO Team Introduction.md|L26-L27|jingzhe zhou email comlocations sg self introduction graduated dalian university
EGO Team Introduction.md|L28-L29|emb joyce teo email sea comlocations sg self introduction joined
EGO Team Introduction.md|L30-L31|junchen li email comlocations bj-qidi-f26-b-p-5 self introduction graduated bachelor degree
EGO Team Introduction.md|L32-L34|portal liufang resigned email maillocations bj-f26-b-o-6 self introduction joined brief
EGO Team Introduction.md|L35-L40|emb mingze wei email comlocations bj-f26-b-p-3 self introduction graduated bachelor
EGO Team Introduction.md|L41-L42|nick yi email comlocations bj-f26-b-q-2 self introduction graduated beihang university
EGO Team Introduction.md|L43-L44|ps emb shanshan jiang resigned email comlocations sg-5spd self introduction
EGO Team Introduction.md|L45-L46|shibin chen email comlocations sg-f5-c6 self introduction joined worked baidu
EGO Team Introduction.md|L47-L48|emb shuquan huang email comlocations sg self introduction joined focusing
EGO Team Introduction.md|L49-L50|ps sixiang yang email comlocations sg self introduction joined graduated
EGO Team Introduction.md|L51-L52|szewen seet email comlocations sg self introduction joined graduated national
EGO Team Introduction.md|L53-L54|tiantian duan email comlocations sg self introduction joined worked data
EGO Team Introduction.md|L55-L56|xiang zhang email comlocations sg self introduction joined worked baidu
EGO Team Introduction.md|L57-L58|xuefeng zhu resigned email comlocations bj-f26-b-p-2 self introduction graduated sjtu
EGO Team Introduction.md|L59-L60|yadong wang email comlocations bj-f26-b-o-5 self introduction joined june worked
EGO Team Introduction.md|L61-L62|yanbin zhao email comlocations sg-f5-c4contact wechat bacoo_zh self introduction joined
EGO Team Introduction.md|L63-L64|yansheng zhang email comlocations bj-qidi-12contact self introduction joined worked bytedance
EGO Team Introduction.md|L65-L66|ps zhijie he email comlocations sg-f5-ab6 self introduction joined worked
EGO Team Introduction.md|L67-L69|shaochen sun email comlocations bj-qidi-f26-b-s-1 self introduction received my master
EGO Team Introduction.md|L70-L72|ss shaoning zheng email locations bj-qidi-f26-b-s-2 self introduction joined join
EGO Team Introduction.md|L73-L75|ss peng liulp email locations bj-qidi-f26 self introduction joined worked
EGO Team Introduction.md|L76-L77|yifan jiang email comlocations bj-qidi-f26 self introduction joined worked kingdee
EGO V0.3.2(GPU train & Colocate train&GNN).md|L3-L4|prd release ss status issues remark requirement gathering done product
EGO V0.3.2(GPU train & Colocate train&GNN).md|L7-L14|mig 模型 训练 cpu gpu 资源 objectives significance colocate gnn
EGO V0.3.2(GPU train & Colocate train&GNN).md|L31-L34|products involved train offline training online learning period
EGO V0.3.2(GPU train & Colocate train&GNN).md|L37-L39|配置 训练 cpu worker a100 gpu 资源 t4 train no
EGO V0.3.2(GPU train & Colocate train&GNN).md|L40-L41|配置 worker ss colocate no page details new job offline
EGO V0_4 API Manual.md|L15-L22|slot emb embedding ss tile pooling using specify sequence length
EGO V0_4 API Manual.md|L23-L44|slot emb embedding category order support share function define concept
EGO V0_4 API Manual.md|L45-L56|slot emb embedding feature ss assign set used graph same
EGO V0_4 API Manual.md|L57-L60|dense feature featuredense training ego gets features directly input samples
EGO V0_4 API Manual.md|L61-L64|emb dense usage dense_emb onehot_emb placeholders shape none more
EGO V0_4 API Manual.md|L65-L68|variable basically same reason why tf placeholder forbidden get_variable instead
EGO V0_4 API Manual.md|L69-L78|usage ego get_variable name shape initializer none optimizer marks unique
EGO V0_4 API Manual.md|L79-L84|emb ss layer module assembled some common modules ego layers
EGO V0_4 API Manual.md|L85-L88|ss ego layers activation class easily constructing module until now
EGO V0_4 API Manual.md|L89-L94|dense ego layers init** self name units kernel_initializer none bias_initializer
EGO V0_4 API Manual.md|L95-L109|ego layers normalization there kinds norm methods supported api standard
EGO V0_4 API Manual.md|L110-L115|emb dense ss ego modules densetower integrates normalizations denses activations
EGO V0_4 API Manual.md|L118-L123|ss label lossweight use ego get_label name label_idx get placeholder
EGO V0_4 API Manual.md|L124-L131|txt format sample label label_weight corresponding relationship formatted multitask label_1
EGO V0_4 API Manual.md|L132-L137|protobuf format sample ego_sample proto label situation ego get_label name
EGO V0_4 API Manual.md|L138-L156|sparse ss round egotf previous init** self name losses loss_weights
EGO V0_4 API Manual.md|L157-L167|ps ss target declaration egotf above pages viewpage action pageid
EGO V0_4 API Manual.md|L168-L178|ps sparse ss offlineround onlineround egotf above pages viewpage action
EGO V0_4 API Manual.md|L179-L192|serving compile ego rounds ego_output auto_editor single round list tuple
EGO V0_4 API Manual.md|L193-L200|serving compile separately training graphs usually consistent use sh model
EGO V0_4 API Manual.md|L201-L208|publish ego-learner checkpoint extra validation step egotf previous publishing model
EGO V0_4 API Manual.md|L209-L214|ps slot emb adf ego config_adf dim adf_key decay_rate related
EGO V0_4 API Manual.md|L217-L222|compile ego add_print items single tensor list tuple tensors function
EGO V0_4 API Manual.md|L223-L226|hdfs ego add_print_vars_to_hdfs egotf above equal add_print func no longer
EGO V0_4 API Manual.md|L227-L232|compile ego add_predict target target_name api add online predict trigger
EGO V0_4 API Manual.md|L233-L236|ego add_print_vars_to_log egotf above print out average value tensor each
EGO V0_4 API Manual.md|L237-L240|ps use tensorboard egotf above pages viewpage action pageid moved
EGO V0_4 API Manual.md|L241-L243|sparse dense feature egotf above ego supports nsc user use
EGO V1.0 Onboarding Process.md|L3-L7|同步 资源 ego 预约 产品 介绍 会议 现状 方法 申领
EGO V1.0 Onboarding Process.md|L8-L19|predictor 训练 样本 离线训练 egopredictor ai_platform-ego_test mfp fs 试用 接入
EGO V1.0 Onboarding Process.md|L20-L39|ps docs google spreadsheets tddy6qtxoyl9zxu6k103vyzwbh7vxooajxkk-esyqa edit gid cmdb l3 ego
EGO V1.0 Onboarding Process.md|L42-L45|seatalk 业务 问题 反馈 群里 产品 负责 识别 哪个 模块
EGO V1.0 Onboarding Process.md|L46-L48|问题 记录 解决 后经 研发 识别 可能 共性 产品 负责
EGO V1.0 online serving alert & monitor.md|L1-L50|monitoring predictor 模型 ps 监控 ss ego infra sz nodeapi
EGO V1.0 online serving alert & monitor.md|L51-L57|ss project management admin list tenant access project-admin tenant-admin edit
EGO portal V0.7.4 PRD.md|L9-L12|配置 emb embedding worker gpu 资源 feature aibox v1 offline
EGO portal V0.7.4 PRD.md|L13-L15|ckpt ps 配置 参数 任务 checkpoint teacher-student offline training period
EGO 性能追查流程.md|L3-L12|配置 cpu sampleserver 日志 worker gpu ss pod grep dailyio
EGO 性能追查流程.md|L13-L16|监控 cpu 带宽 ss request pod batch_buffer_queue_size ins_queue_size shuffle_queue_size read_threads
EGO 性能追查流程.md|L17-L20|日志 内存 ss memory pod ss_batch_buffer_size dailyio 优化 挑选 识别
EGO 性能追查流程.md|L21-L31|监控 配置 调优 cpu 参数 日志 timestamp mem pod 优化
EGO 智能问答机器人项目v1.md|L1-L47|配置 资源 incomplete dod 背景 目标 项目 当前 用户 沟通
EGO 智能问答机器人项目v1.md|L48-L71|portal scope rag qa out v2 项目 范围 搭建 支持
EGO 智能问答机器人项目v1.md|L72-L74|上线 部署 timeline milestones step ref mvp 项目 阶段 计划
EGO 智能问答机器人项目v1.md|L75-L77|模型 risks mitigations 风险管理 风险 等级 应对 措施 文档 结构
EGO1_0 NSC_Negative Sample Center* user manual.md|L5-L10|dense feature ego get*dense_feature add use_nsc true param api indicates
EGO1_0 NSC_Negative Sample Center* user manual.md|L11-L16|slot sparse ego get*slots adding use_nsc true parameter indicates input
EGO1_0 NSC_Negative Sample Center* user manual.md|L17-L20|sample format nsc needs category item*id info users wants use
EGO1_0 NSC_Negative Sample Center* user manual.md|L21-L26|sparse converter dense feature txt format py category item*id should
EGO1_0 NSC_Negative Sample Center* user manual.md|L27-L32|protobuf format case user should add item*id category ext field
EGO1_0 NSC_Negative Sample Center* user manual.md|L33-L39|ego-learner feature yaml config file users specify many nsc-related configurations
EGOPortal V0.1.0 Overview Design.md|L8-L13|portal 训练 推理 任务 稀疏 版本 objectives significance egoportal ego
EGOPortal V0.1.0 Overview Design.md|L18-L19|ps emb ss range user permissions module name target member
EGOPortal V0.1.0 Overview Design.md|L24-L59|emb 任务 member management batch ego admin project tenant 平台
EGOPortal V0.1.0 Overview Design.md|L62-L105|编译 模型 训练 任务 compile offline learning mvp ego model
EGOPortal V0.1.0 Overview Design.md|L106-L119|训练 同步 kafka 参数 稀疏 checkpoint hdfs online learning tbd
EGOPortal V0.1.0 Overview Design.md|L120-L127|portal predictor 模型 ps 发布 训练 推理 资源 ss creating
EGOPortal V0.1.0 Overview Design.md|L128-L131|模型 发布 训练 model management 贯穿 整个 业务 周期 模块
EGOPortal V0.1.0 Overview Design.md|L132-L139|编译 模型 发布 训练 任务 版本 offline model management ego
EGOPortal V0.1.0 Overview Design.md|L140-L151|灰度发布 模型 ps 发布 配置 特征 release model validation samples
EGOPortal V0.1.0 Overview Design.md|L152-L165|回滚 模型 监控 发布 日志 版本 online model management 完成
EGOPortal V0.1.0 Overview Design.md|L166-L174|模型 ps 监控 发布 训练 任务 worker 资源 devops job
EGOPortal V0.1.0 PRD.md|L7-L29|ss products involved permission management reuse batch platform permissions model
EGOPortal V0.1.0 PRD.md|L32-L49|ss platform architecture overall framework ego designed follow permission management
EGOPortal V0.1.0 PRD.md|L54-L85|emb ss function description users use company google mail log
EGOPortal V0.1.0 PRD.md|L90-L125|ss function description model users enters platform located under management
EGOPortal V0.1.0 PRD.md|L126-L131|field description model name required editable front-end form restrictions input
EGOPortal V0.1.0 PRD.md|L132-L141|prototype screenshots model version job list
EGOPortal V0.1.0 PRD.md|L144-L167|evict checkpoint function description generating training job one most important
EGOPortal V0.1.0 PRD.md|L168-L169|field description name required front-end form restrictions input box maximum
EGOPortal V0.1.0 PRD.md|L178-L186|serving emb publish ss function description completed training published results
EGOPortal V0.1.0 PRD.md|L191-L192|country enumeration values abbreviations rgb indonesia ed8ce vn viet nam
EGOPortal V0.1.0 Requirements List.md|L7-L23|sparse feature ss goals complete functionality supports training large scale
EGOPortal V0.1.0 Requirements List.md|L28-L29|portal emb ss egoportal requirements list module name requirement description
EGOPortal V0.1.2 问题记录.md|L37-L54|模型 发布 release checkpoint sure replace old one type new
EGOPortal V0.1.2 问题记录.md|L55-L93|ckpt deepctr ps 发布 训练 sparse keys count mf model
EGOPortal V0.1.3 PRD.md|L3-L15|portal ckpt 模型 发布 训练 推理 上线 离线训练 checkpoint feature
EGOPortal V0.1.3 PRD.md|L30-L41|ckpt 训练 checkpoint load project offline training job tenant-project model
EGOPortal V0.1.3 PRD.md|L42-L77|ckpt 模型 ps slot emb worker feature model key dd
EGOPortal V0.1.3 PRD.md|L80-L95|ckpt 发布 online model live liveish s3 rollback 支持 选择
EGOPortal V0.1.3 PRD.md|L96-L115|ckpt predictor 发布 project online model tenant-project version offline training
EGOPortal V0.2.0 PRD.md|L5-L29|发布 serving checkpoint products involved online learning job list new
EGOPortal V0.2.0 PRD.md|L36-L51|eval 任务 offline training list new job type train evaluation
EGOPortal V0.2.0 PRD.md|L56-L70|发布 serving release online learning job list training new name
EGOPortal V0.2.0 PRD.md|L71-L78|配置 kafka new online learning job batch training data source
EGOPortal V0.2.0 PRD.md|L79-L98|eval checkpoint online learning job detail tasks sub jobs monitor
EGOPortal V0.2.0 PRD.md|L99-L104|发布 任务 release online learning job list operation batch sync
EGOPortal V0.2.0 PRD.md|L107-L114|serving 部署 online model list status description operation created lock
EGOPortal V0.2.0 PRD.md|L115-L122|配置 serving 部署 update online model env name deploying failed
EGOPortal V0.2.0 PRD.md|L127-L155|训练 任务 period training rule list one-time batch name job
EGOPortal V0.2.0 PRD.md|L156-L169|发布 配置 训练 参数 任务 checkpoint hdfs new period training
EGOPortal V0.2.0 PRD.md|L170-L180|任务 资源 period training list tenant project status description operation
EGOPortal V0.2.0 PRD.md|L181-L199|训练 converter feature update verify start period training rules desc
EGOPortal V0.2.0 PRD.md|L200-L220|ckpt 同步 任务 publish release checkpoint 版本 period training list
EGOPortal V0.2.1 PRD.md|L1-L30|ckpt release delete confirmation ai model version training job stop
EGOPortal V0.2.1 PRD.md|L31-L36|任务 creator modify job model sub jobs training copy 因为
EGOPortal V0.2.1 PRD.md|L37-L42|配置 资源 copy job training name project 功能 主要 服务
EGOPortal V0.2.1 PRD.md|L43-L50|wc cpu coordinator 内存 job resource management page count work
EGOPortal V0.2.1 PRD.md|L61-L76|配置 version code job model py used modifying configuration may
EGOPortal V0.2.1 PRD.md|L85-L88|训练 日志 ui job pod info warning 优化 显示 提供
EGOPortal V0.2.1 PRD.md|L89-L110|emb project management admin member tenant resource job setting alert
EGOPortal V0.2.1 PRD.md|L111-L126|emb checkpoint hdfs project management each archive up checkpoints same
EGOPortal V0.2.1 PRD.md|L127-L134|ps 发布 训练 任务 checkpoint model version link docs google
EGOPortal V0.2.1 PRD.md|L139-L144|eval train type controller ui ego*train_mode offline training job evaluation
EGOPortal V0.2.2 PRD.md|L11-L18|参数 job task batch error vn-h1 tech link 链接 失败
EGOPortal V0.2.2 PRD.md|L19-L34|serving 上线 offline online project admin creator unlock delete status
EGOPortal V0.2.2 PRD.md|L35-L44|ckpt 模型 serving 训练 任务 版本 model management version list
EGOPortal V0.2.2 PRD.md|L45-L48|ps onlineps release offlineps task train completed training start pending
EGOPortal V0.2.2 PRD.md|L49-L70|portal 配置 训练 任务 版本 diff version info code file
EGOPortal V0.2.2 PRD.md|L71-L74|任务 job pending offline train period resource management 支持 自定义
EGOPortal V0.2.2 PRD.md|L79-L88|ego alert management ot pt ol 周期性 调度 增加 报警
EGOPortal V0.2.2 PRD.md|L89-L102|slot sparse feature clear_nn_grad optimizer load these slots grads fliter
EGOPortal V0.2.2 PRD.md|L103-L118|tensorboard ui job view click here check related tensorboards automatically
EGOPortal V0.2.2 PRD.md|L119-L124|发布 serving converter compile publish online config file note allow
EGOPortal V0.2.2 PRD.md|L125-L140|发布 任务 ss ego round auc job block running start
EGOPortal V0.2.2 PRD.md|L141-L158|serving 训练 worker 资源 job list personal all model creator
EGOPortal V0.2.2 PRD.md|L159-L192|ps 日志 more usage information please refer wiki user debug
EGOPortal V0.2.2 PRD.md|L193-L232|编译 ps ego-train gnn server naming controller redis git garena
EGOPortal V0.2.2 PRD.md|L233-L240|配置 任务 worker ss autokill 报警 策略 默认值 如上 默认
EGOPortal V0.2.2 PRD.md|L241-L245|ckpt ps ss hdfs size please note gb below represents
EGOPortal V0.3.0 PRD.md|L5-L34|ckpt 回滚 灰度发布 predictor presstest 监控 发布 serving ss products
EGOPortal V0.3.0 PRD.md|L39-L51|presstest inferencing serving release ss batch training list online export
EGOPortal V0.3.0 PRD.md|L52-L81|ckpt predictor 发布 serving 任务 release new batch model overview
EGOPortal V0.3.0 PRD.md|L82-L97|ckpt 配置 serving release update batch training list name project
EGOPortal V0.3.0 PRD.md|L98-L114|monitoring ckpt 回滚 监控 发布 serving 日志 版本 batch model
EGOPortal V0.3.0 PRD.md|L115-L175|发布 配置 serving release 版本 canary config online model grey
EGOPortal V0.3.0 PRD.md|L178-L183|predictor presstest serving 任务 ss ego ip batch model online
EGOPortal V0.3.0 PRD.md|L184-L189|presstest 任务 部署 ss list status description operation waiting cancel
EGOPortal V0.3.0 PRD.md|L190-L227|presstest 配置 serving cpu 参数 gpu ss new batch model
EGOPortal V0.3.0 PRD.md|L228-L241|presstest 发布 配置 serving 任务 资源 ss view info result
EGOPortal V0.3.0 PRD.md|L242-L256|ckpt ps evict 发布 配置 serving release feature ss admission
EGOPortal V0.3.0 PRD.md|L259-L276|online export job cancelled list status description operation waiting stop
EGOPortal V0.3.0 PRD.md|L277-L288|任务 job page new layout offline training train list info
EGOPortal V0.3.0 PRD.md|L289-L294|配置 参数 checkpoint greedy load mode train tab want add
EGOPortal V0.3.0 PRD.md|L297-L301|predictor serving release 版本 project offline list job push end
EGOPortal V0.3.1 PRD.md|L1-L82|ckpt 监控 发布 配置 训练 任务 ss changes nsc yaml
EGOPortal V0.3.1 PRD.md|L85-L93|ckpt 回滚 模型 发布 配置 serving 训练 半精度 任务 products
EGOPortal V0.3.1 PRD.md|L98-L105|monitoring ckpt predictor ps serving batch training list type env
EGOPortal V0.3.1 PRD.md|L106-L137|ckpt 配置 serving emb checkpoint new batch model one-checkpoint period-checkpoint
EGOPortal V0.3.1 PRD.md|L138-L232|ckpt 配置 serving emb batch model basic information info list
EGOPortal V0.3.1 PRD.md|L233-L238|serving others offline name log 优化 操作 二次 验证 其他
EGOPortal V0.3.1 PRD.md|L241-L247|serving 部署 online learning list status description operation created update
EGOPortal V0.3.1 PRD.md|L248-L264|发布 serving release new online learning list basic info name
EGOPortal V0.3.1 PRD.md|L265-L270|ckpt 灰度发布 发布 配置 serving 参数 release update online learning
EGOPortal V0.3.1 PRD.md|L271-L282|monitoring 监控 serving online learning basic information model detail info
EGOPortal V0.3.1 PRD.md|L285-L319|notification management ui ux list page ego live uat noti
EGOPortal V0.3.1 PRD.md|L320-L329|release project management offline view operation records all tenant 支持
EGOPortal V0.3.1 PRD.md|L330-L339|ckpt management tab project all-- lists aggregated creator model tenant
EGOPortal V0.3.1 PRD.md|L340-L345|project management-dashboard 红色 两个 看板 去掉 下面 黄色 过去 因为
EGOPortal V0.3.1 PRD.md|L348-L351|portal 配置 ego-learner support nsc negative sample center yaml 相关
EGOPortal V0.3.1 PRD.md|L352-L381|portal 发布 serving 训练 任务 hdfs period training job ui
EGOPortal V0.3.1 PRD.md|L382-L393|ckpt 模型 监控 训练 release ss half precision auc alert
EGOPortal V0.3.1 PRD.md|L394-L399|checkpoint feature load parameter nn train management-- import paramter filter
EGOPortal V0.3.1 PRD.md|L400-L419|ckpt serving checkpoint model list edit version batch training job
EGOPortal V0.3.1 PRD.md|L420-L426|train job config files 优化 调整 三种 详情页 部分 字段
EGO优化项使用盘点清单.md|L5-L11|ps docs google spreadsheets fwac739vxs36rw6jnd0ml1zbfcc99e20q-ewmqlnfzw edit gid 优化 盘点
EGO性能参数汇总.md|L1-L17|sampleserver worker minibatch sample_server 内存 ss read_threads max_daily_io_num max_daily_io_num_on_worker ss_batch_buffer_size
EGO性能参数汇总.md|L18-L22|max_context_per_device 磁盘 max_session_per_device worker minibatch 内存 ss 耗时 worker_batch_buffer_size get_batch
Ego 1_0 Performance Comparison.md|L2-L8|deepctr ps benchmark hdfs ego vs deeprec train days samples
Ego 1_0 Performance Comparison.md|L9-L14|ps benchmark hdfs din train days samples model files ttps
Ego 1_0 Performance Comparison.md|L15-L20|deepctr ps cpu worker 资源 ss ego v1 vs tensornet
Ego 1_0 and 0_4 AUC Comparison.md|L1-L10|deepctr ps model train days samples auc curves basically overlapped
Ego 1_0 and 0_4 AUC Comparison.md|L11-L19|ps din model train days samples auc curves basically overlapped
Ego 1_0 and 0_4 AUC Comparison.md|L20-L31|ps nl9_pdpv4_fpv2_f4 model train days samples auc curves basically overlapped
Ego 1_0 and 0_4 AUC Comparison.md|L32-L43|ps shopv5d2_sppt_din_parquet_dyx_on_sg train days samples auc curves basically overlapped model
Ego 1_0 and 0_4 AUC Comparison.md|L44-L56|ps nl8_pdpv5_4 train days samples auc curves basically overlapped model
Ego 1_0 and 0_4 AUC Comparison.md|L57-L69|ps sparse sparsednn_adf train days samples auc performance ego better
Ego 1_0 and 0_4 AUC Comparison.md|L70-L81|ps feature nl9_pdpv4_parquet train days samples auc performance ego better
Ego 1_0 with_without nsc code AUC Comparison.md|L1-L7|portal deepctr ps ego-portal train day samples master job live-test
Ego 1_0 with_without nsc code AUC Comparison.md|L8-L15|ckpt ps sparse hdfs nl8-pdv5 load r2 projects mlp_ego dev
Ego 1_0 with_without nsc code AUC Comparison.md|L16-L25|ckpt ps feature hdfs shopv5d2-sppt-din-parquet-dyx load r2 projects rcmd_feature prod
Ego Controller 1_0 使用文档.md|L20-L26|get model list uri scope project current pagesize 取值 当前
Ego Controller 1_0 使用文档.md|L36-L41|get model versions list uri current version pagesize 获取 第几页
Ego Controller 1_0 使用文档.md|L65-L69|checkpoint get list uri current checkpoints pagesize 获取 第几页 开始
Ego DataPlugin_Depreciated*.md|L1-L20|converter feature ss introduction during training ego support use user-defined
Ego DataPlugin*Depreciated*.md|L21-L38|slot converter ss data plugins reassignment plugin change another data-plugin
Ego DataPlugin*Depreciated*.md|L39-L52|train*config ego-learner step use data plugins specify lib path yaml
Ego DataPlugin_Depreciated*.md|L53-L78|ego-train step customize data plugins start docker following instruction sudo
Ego DataPlugin*Depreciated*.md|L79-L94|feature ss parallelization online services one request often contains multiple
Ego DataPlugin*Depreciated*.md|L95-L103|predictor ps serving tips online config plugin export online*export_config ego_plugin_path
Ego Design Doc v0_1.md|L1-L26|ps purpose document designed ego parameter-server li paradigm training framework
Ego Design Doc v0_1.md|L29-L55|ps worker concept vocabulary parameter server group node stores part
Ego Design Doc v0_1.md|L56-L91|ps ss architecture ego designed traditional paradigm discuss key ideas
Ego Design Doc v0_1.md|L92-L143|ps emb embedding feature key features ego tf graph core
Ego Design Doc v0_1.md|L144-L150|gpu roadmap ego supporting more flexible metadata control standard algorithm
Ego Design Doc v0_1.md|L151-L160|deepctr ps examples deep ctr youtube rank model research google
Ego Design Doc v0_1.md|L161-L167|develop plan coding complete testing dd beta version programmers yanbin
Ego Design V1_0.md|L1-L4|ps ego introduction docs google presentation ejjlyve3d6mixrtzlxnkublwr49z2bauxzqq5ffl0qe edit slide g20a8007fedf_0_200
Ego Design V1_0.md|L5-L8|ps whole design ego v1 docs google document pw4okfmum_l63hr0ci4c31lo08nvfl0lkjmvadmexc8
Ego Design V1_0.md|L9-L12|egotrain ps v1 design dev plan docs google document c2xge3qmva8izrzekm-cldzyqg3wwyi9_vrmechzkh4
Ego Design V1_0.md|L13-L16|ps egops v1 design dev plan docs google document vtdltpzhod6jpcnshkqo-riw6yurigpjzwkculws3py
Ego Design V1_0.md|L17-L22|predictor ps egopredictor v1 design dev plan docs google document
Ego Design V1_0.md|L23-L28|ps egocontroller v1 design docs google document btv8nzmjhgiuhjhdq09obkxrv82ufk5oqkbctvp4wp0 dev plan
Ego Design V1_0.md|L29-L32|ps negative sample center design docs google document uym-yi9ikqwkvdbrzwwqpuplr0vh58qkyuf4n9tjxk
Ego Design V1_0.md|L33-L35|ps online learning design docs google document el-gugc7jc909rwy6zmtmj8gyo9tkrlpb0jge8mgvbo
Ego FAQ.md|L14-L17|controller pic- yadong wang mailto
Ego FAQ.md|L18-L23|ckpt ps checkpoint hdfs q1 why my deleted prevent being
Ego FAQ.md|L24-L30|checkpoint ss q2 why am unable delete version only versions
Ego FAQ.md|L31-L38|notebook q3 why open there several common reasons just created
Ego FAQ.md|L39-L46|notebook q4 print tensor define function graph dependencydef print_tensor input
Ego FAQ.md|L47-L52|a30 gpu q5 submit training job should choose project want
Ego FAQ.md|L53-L64|ps ss q6 why my job stuck prealloc_mem task allocation
Ego FAQ.md|L65-L70|ps offlineps ss q7 trying submit train job error message
Ego FAQ.md|L71-L86|q8 questions using periodic training start my rule fill last
Ego FAQ.md|L87-L90|serving q9 prevent my being offline no traffic time needs
Ego FAQ.md|L97-L100|monitoring grafana ss q11 should turn ego new colleague usually
Ego FAQ.md|L101-L112|ss q12 apply ego permissions memeber role business connected please
Ego FAQ.md|L113-L142|ckpt ps 同步 跨机房 publish checkpoint offlineps ss q13 across
Ego FAQ.md|L143-L170|配置 训练 任务 q14 set up relatively complex period rules
Ego FAQ.md|L171-L175|ss perf pic- zhijie he mailto does dod any ideas
Ego Full Configuration Preview.md|L9-L32|hdfs environment setting egotf ego thread_num shell_verbose false whether show
Ego Full Configuration Preview.md|L33-L40|batch_size minibatch batch size training minibatch_size
Ego Full Configuration Preview.md|L41-L44|sparse feature elimination
Ego Full Configuration Preview.md|L47-L50|feature method unseen day exceeded delete_after_unseen_days right now train model
Ego Full Configuration Preview.md|L55-L60|feature score show clk nonclk_coeff clk_coeff max unseen_days
Ego Full Configuration Preview.md|L65-L230|ckpt converter worker hdfs whether shuffle all samples between workers
Ego Full Configuration Preview.md|L231-L248|slot emb deprecated mf_plugin controls updated rules mf_emb dim lr_emb
Ego Full Configuration Preview.md|L249-L262|emb deprecated lr_plugin controls updated rules lr_emb dim fixed mf_emb
Ego Full Configuration Preview.md|L263-L268|feature cvm_plugin counts show time click each key decay rate
Ego Full Configuration Preview.md|L269-L282|adf_plugin accumulate adf_vector each sample capture user habits plugin_used true
Ego Full Configuration Preview.md|L283-L294|feature ss use tf backend must configured tf_plugin use_multi_task true
Ego OnlinePS User Manual.md|L1-L6|ps emb onlineps embedding introduction distributed multi-replica in-memory service used
Ego OnlinePS User Manual.md|L9-L12|ps emb onlineps embedding publish ss egov0 model publishing process
Ego OnlinePS User Manual.md|L13-L24|emb things prepare model trained least ego-api version online-export yaml
Ego OnlinePS User Manual.md|L25-L42|ps worker submit push-to-online-ps job push_to_online_ps sh script could obtained
Ego OnlinePS User Manual.md|L43-L54|ps get status push-to-online-ps job get_status_of_online_ps sh script could obtained
Ego OnlinePS User Manual.md|L55-L58|predictor receive requests country online_export_path parameters specified user script determine
Ego Predictor Guardian.md|L5-L28|同步 资源 内存 etcd master schedule cluster_schedule meta api k8sapi
Ego Predictor Guardian.md|L29-L51|cpu 部署 资源 master clustera meta etcd clustermeta cluster memory
Ego Predictor Guardian.md|L52-L61|cpu 内存 memory hugepage scheduleproperty master etcd meta cluster clustera
Ego Predictor Guardian.md|L62-L73|模型 ps cpu benchmark 部署 gpu 资源 内存 master qps
Ego Predictor Guardian.md|L74-L77|模型 版本 doublebuffer 更新 只是 日常 这时 我们 采用 切换
Ego Predictor Guardian.md|L78-L83|predictor 模型 配置 k8s server graceful unregister ns maxunavailable maxsurge
Ego Predictor Guardian.md|L84-L101|模型 同步 内存 schedule master meta api k8sapi server clustermeta
Ego Predictor Guardian.md|L102-L109|模型 client master slave server zk ram namingservice instance channel
Ego Predictor Guardian.md|L110-L115|模型 ps cpu 显存 gpu 内存 t4 pod 路由 算法
Ego Predictor Guardian.md|L118-L124|模型 部署 gpu pod 功能 目标 粒度 主要 同时 支持
Ego Predictor Guardian.md|L125-L131|cpu gpu mem 功能 目标 充分利用 可用 高性能 用户 学习
Ego Predictor Guardian.md|L132-L139|资源 ss business model pod line busygroup idlegroup 概念 抽象
Ego Predictor Guardian.md|L140-L146|ego-predictor predictor 模型 cpu gpu ego-predictor-master memory 问题 困难 避免
Ego Predictor Guardian.md|L149-L166|predictor l4 egopredictor input set k8s deployments egopredictor-bdl-live-sg egopredictor-bdl-liveish-sg mid
Ego Predictor Guardian.md|L167-L173|output sequence instructions following type scale line deployment capacity changes
Ego Predictor Guardian.md|L174-L259|algo algo-1 move pods between busy lines while keeping capacity
Ego Sample.md|L35-L59|parquet format develop program generating training data should refer schema
Ego Sample.md|L60-L72|converter hdfs provide two ways convert sample data method1 script
Ego Support Serving's Multiple Versions Online At the Same Time.md|L1-L10|发布 serving 版本 ego api ui 前置 说明 级别 支持
Ego Validator.md|L3-L8|feature input model path such model_path must include sample dat
Ego Validator.md|L9-L12|get validator stored docker container pull image like
Ego Validator.md|L15-L24|publish ss prepare model notice must liveish without validation set
Ego Validator.md|L25-L36|feature set gflag model_path path model include sample dat print_features
Ego Validator.md|L37-L46|feature example docker container validator under directory bin model file
Ego Validator.md|L47-L62|feature check result predict score validator sample using model original
Ego Weekly Reports.md|L1-L6|resolve training two-towers model optimise yarn job ego avoiding crash
Ego Weekly Reports.md|L7-L11|support generate tensorflow graph model_conf json two-towers model complete make
Ego Weekly Reports.md|L12-L17|publish adjust output format each layer under debug mode support
Ego Weekly Reports.md|L18-L22|ego data_io support huge sample data complete proto format supports
Ego Weekly Reports.md|L23-L27|ego supports tensorflow development finishes start test auc high one
Ego Weekly Reports.md|L28-L32|ego supports tensorflow fix bugs bn layer works normally avoiding
EgoBox_gpu pull优化*性能测试.md|L3-L38|round0 round1 磁盘 任务 gpu 耗时 版本 dsrm*v552 ins pull
EgoBox_gpu pull优化*性能测试.md|L39-L74|round0 round1 训练 任务 gpu 耗时 版本 cvr*v21_delay_br ins pull
EgoBox_gpu pull优化*性能测试.md|L75-L117|round0 round1 训练 任务 gpu 耗时 版本 cart*unify round2 ins
EgoBox设计与优化点摸排.md|L1-L11|slot feature ss endminipass rehash beginminipass slot_group stack_by_slot minipass batchfea
EgoMP api方案第三版.md|L1-L4|模型 sparse pytorch ego metric api 接口 说明 原则 尽量
EgoMP api方案第三版.md|L5-L6|训练 参数 ego-learner ego init_train_thread cls model torch nn module
EgoMP api方案第三版.md|L7-L10|训练 参数 pytorch dataset dataloader ego init\_\_ day xxxx learner
EgoMP api方案第三版.md|L11-L12|参数 ss metric ego target name click type metrictype auc
EgoMP api方案第三版.md|L13-L16|slot 参数 sparse dense feature label weight inittrainconfig ego get_slots
EgoMP api方案第三版.md|L17-L20|参数 sparse optimizer nn ego config_lr config_mf config_adf defaultsparseoptimizer lr
EgoMP api方案第三版.md|L21-L22|ps evict 参数 ego dump decay 相关 接口定义 说明 语义
EgoMP api方案第三版.md|L23-L26|nsc listwise dumptensor local_debug bn 其他 相关 等等 待定
EgoMP api方案第三版.md|L27-L29|deepctr ps 训练 gpu demo pytorch github examples blob main
EgoMP api方案第二版.md|L1-L4|模型 sparse pytorch ego metric api 接口 说明 原则 尽量
EgoMP api方案第二版.md|L5-L14|训练 参数 worker ss pytorch dataset dataloader ego day pass_control
EgoMP api方案第二版.md|L15-L16|参数 metric ego target name click type metrictype auc round_idx
EgoMP api方案第二版.md|L17-L18|slot 参数 sparse dense feature ego get_slots name sparse_input slots
EgoMP api方案第二版.md|L19-L24|配置 slot 参数 sparse optimizer nn config_lr config_mf config_adf add_slots_optimizers
EgoMP api方案第二版.md|L25-L26|ps 配置 训练 参数 sparse ego starttrain ego_config pb json
EgoMP api方案第二版.md|L27-L30|nsc listwise dumptensor local_debug bn 其他 相关 等等 待定
EgoMP效果对齐记录.md|L1-L3|cpu 参数 sparse 任务 nn mf base 整体 结论 影响
EgoMP效果对齐记录.md|L6-L16|slot emb embedding sparse 特征 lr mf tf only base
EgoMP效果对齐记录.md|L17-L26|emb 参数 embedding sparse mf lr nn truncated_normal std two
EgoMp初版性能评估测试.md|L1-L9|ps ss 耗时 xla search_prerank_bert tbackend tf avg ms torch
EgoMp初版性能评估测试.md|L10-L16|deepctr cpu 耗时 版本 torch tf h17m vs backend run
EgoPS限流规则*功能上线后会将文档翻译成英文*.md|L3-L12|ps 告警 限流 server redis client 原理 如图所示 实现 分为
EgoPS限流规则*功能上线后会将文档翻译成英文*.md|L15-L20|cpu 限流 shard thre speed min max 基于 利用率 管控
EgoPS限流规则*功能上线后会将文档翻译成英文*.md|L21-L23|限流 shard 集群 基本 单位 细粒度 控制 同一个 不同 可能
EgoPlugin slot does not map_duplicate.md|L1-L4|监控 slot egoplugin duplicate map 问题 遇到 没有 或则 情况
EgoPlugin slot does not map_duplicate.md|L5-L14|cpp_converter 模型 slot sparse converter sparseextractor kept_sparse_slots plugin dst_slot src_slot
EgoPlugin*实现自定义指标指导.md|L9-L12|配置 参数 egoplugin ego-plugin yaml plugin metricplugin 文件 模块 统一
EgoPlugin*实现自定义指标指导.md|L13-L22|egotrain 配置 训练 custommetricgroup custom_metric_group cc factory_register metric ginimetric const
EgoPlugin*实现自定义指标指导.md|L23-L33|配置 metric ginimetric metricplugin target gini*metric cc ego-plugin-v1 core plugin
EgoPlugin*实现自定义指标指导.md|L34-L58|向量 worker bucketmetric reduce double reduceop sum mean max createlocalbuckets
EgoPlugin*实现自定义指标指导.md|L61-L93|配置 样本 特征 dense group_id addonesample ads int64_is_ads metric_config 实现
EgoPlugin*实现自定义指标指导.md|L94-L96|模型 配置 target ego-plugin yaml metricplugin test*target1 test_target2 metrictype custom
EgoPredictor User Manual.md|L5-L14|predictor ps egopredictor service proto upservice predict method git garena
EgoPredictor User Manual.md|L19-L26|predictor egopredictor ss usage go grpc zk thanks william eka
EgoPredictor User Manual.md|L27-L30|usage go grpc dns recommend once cluster deployed ask wyatt
EgoPredictor User Manual.md|L31-L34|usage json debug body recommend online using convenient offline
EgoPredictor User Manual.md|L35-L51|predictor egopredictor usage pb no rpc framework brpc grpc eg
EgoPredictor X Qir.md|L1-L342|predictor 模型 tensorrt 推理 显存 gpu 内存 负载均衡 predictor-proxy python
EgoPredictor X Qir.md|L343-L348|predictor ps egopredictor ss sg soc project service stateless-service current
EgoPredictor X Qir.md|L349-L356|monitoring predictor ps 监控 grafana gpu egopredictor sg infra sz
EgoPredictor X Qir.md|L357-L363|portal 模型 ps 发布 ego-portal ego workspace 流程 暂时 无法
EgoPredictor brpc Client_for Recommendation*.md|L7-L12|predictor set gflag ego*predictor_client_redis_key each service unique cluster configuration specify
EgoPredictor brpc Client_for Recommendation*.md|L15-L18|predictor egopredictor link client available srec*dd_basis
EgoPredictor brpc Client_for Recommendation*.md|L19-L21|redis server available down set client*options redis_key empty thus all
EgoPredictor.md|L3-L12|feature module dependency up mainly used predict score feed some
EgoTF Alpha Version.md|L1-L5|requirements tensorflow version use tf float32 all params variables avoiding
EgoTF Alpha Version.md|L6-L9|hdfs sdk r2 projects dd dev mpi pkg egotf-sdk-0 alpha
EgoTF Alpha Version.md|L10-L16|slot sparse dense feature samples format sample_id x1 x2 onehot
EgoTF Alpha Version.md|L17-L34|deepctr demo usage define model refer py generate graph pb
EgoTF Beta Version.md|L1-L4|hdfs requirements tensorflow version sample data model output should located
EgoTF Beta Version.md|L5-L12|ps ss hdfs sdk r2 projects dd dev mpi pkg
EgoTF Beta Version.md|L13-L18|ps ss dev machine use smc-toc login example sse account
EgoTF Beta Version.md|L19-L22|samples more info organise sample data format please refer
EgoTF Beta Version.md|L23-L32|slot sparse dense feature text format sample_id x1 x2 onehot
EgoTF Beta Version.md|L33-L39|ps protobuf format ego_sample proto please refer definition pb_tools git
EgoTF Beta Version.md|L42-L70|deepctr compile train optional init python env source env_init sh
EgoTF Beta Version.md|L71-L78|deepctr emb embedding sparse ss hdfs build edit demo emb-build
EgoTF Beta Version.md|L79-L84|ckpt deepctr publish ss hdfs pack model related resources python
EgoTrain Extensions.md|L11-L29|ps slot emb embedding ss cel-plugin draft version1 background cel
EgoTrain Extensions.md|L30-L49|converter ss cei-plugin draft2 running sample server customizeddataconverterplugin initialisation function
EgoTrain Extensions.md|L50-L60|ss egoplugin new each user may customised demands process reading
EgoTrain Extensions.md|L61-L70|sampleserver converter ego-plugin yaml user_define_config_file path user-defined configure file sampleserverplugin
EgoTrain Extensions.md|L71-L77|sampleserver ss sampleserverplugin init initialised function libego-plugin loaded ego_plugin_config_path path
EgoTrain Extensions.md|L78-L97|slot worker ss workerplugin init initialised function libego-plugin loaded ego_plugin_config_path
EgoTrain Extensions.md|L98-L108|wc coordinator ss coordinatorplugin init initialised function libego-plugin loaded ego_plugin_config_path
EgoTrain V0_4 User Manual.md|L1-L6|slot sparse checkpoint feature hdfs know tensorflow python key sign
EgoTrain V0_4 User Manual.md|L7-L18|ps release ss api sdk latest version please refer access
EgoTrain V0_4 User Manual.md|L19-L22|ps dev machine now no apply special develop model submit
EgoTrain V0_4 User Manual.md|L23-L26|samples more info organise sample data format please refer
EgoTrain V0_4 User Manual.md|L27-L36|slot sparse dense feature text format sample_id x1 x2 onehot
EgoTrain V0_4 User Manual.md|L37-L43|ps protobuf format ego_sample proto please refer definition pb_tools git
EgoTrain V0_4 User Manual.md|L46-L76|deepctr ps compile train define model refer ego_api demo deepctr_model
EgoTrain V0_4 User Manual.md|L77-L81|ps emb onlineps embedding sparse publish build pack ego_ver please
EgoTrain XLA GPU backend.md|L1-L8|compile xla background tensorflow accelerated linear algebra compiler boost execution
EgoTrain XLA GPU backend.md|L9-L16|compile gpu xla introduction order accelerate ego training speed developed
EgoTrain XLA GPU backend.md|L17-L26|egotrain train_config ego-learner xla instructions image pls use tf2 config
EgoTrain XLA GPU backend.md|L27-L40|portal ps benchmark release ego-portal analysis take dsrm model example
EgoTrain XLA GPU backend.md|L43-L48|cpu compile xla batchsize distribute opt compilation extremely intensive time
EgoTrain XLA GPU backend.md|L49-L54|egotrain mig ss xla correctness most users using means user
EgoTrain XLA GPU backend.md|L55-L64|mig ss tf1 tf2 most existing models based ego tf
EgoTrain XLA GPU backend.md|L67-L75|ps compile xla other references git garena ego direct_xla blob
EgoTrain metrics.md|L6-L79|cpu worker engineer metrics engineers check time cost execution each
EgoTrain metrics.md|L80-L124|user metrics egotf v0 collects below help users view model
EgoTrain scripts with openapi.md|L1-L15|ego_learner worker submit job cluster openapi method train_k8s_openapi sh tenant_name
EgoTrain scripts with openapi.md|L16-L19|deepctr emb feature submit job specified ego version train_k8s sh
EgoTrain scripts with openapi.md|L20-L27|get job status get_status_k8s_openapi sh tenant_name project_name job_id admin false
EgoTrain scripts with openapi.md|L28-L34|list jobs under account list_jobs_openapi sh tenant_name project_name status name
EgoTrain scripts with openapi.md|L35-L42|get job log get_log_k8s_openapi sh tenant_name project_name job_id env test
EgoTrain scripts with openapi.md|L43-L52|enter pod job debug debug_k8s_openapi sh tenant_name project_name job_id env
EgoTrain scripts with openapi.md|L53-L68|ego_learner emb worker submit emb-builder task openapi method execute emb-build
EgoTrain scripts with openapi.md|L69-L74|ss delete job stop_k8s_openapi sh tenant project job_id note stop
EgoTrain scripts with openapi.md|L75-L77|view job info debug get_job_info_openapi sh tenant_name project_name job_id admin
EgoTrainV1 Disk Management_Depreicated*.md|L1-L4|target ego v1 generated batchfea prioritized stored memory transfer disk
EgoTrainV1 Disk Management*Depreicated*.md|L5-L18|wc sampleserver worker ss primary responsibility parse data files supply
EgoTrainV1 Disk Management*Depreicated*.md|L19-L38|sampleserver worker ss there three main process prefetch request batchfea
EgoTrainV1 IO module update.md|L10-L21|egotrain 训练 sampleserver worker 资源 coordinator workercoordinator dailyio batchfea ego
EgoTrainV1 IO module update.md|L24-L29|训练 sampleserver worker batchfea string batchparserbatchfeadiskcontrol loadbatchfea getbatchfeafromsampleserver 减少 之间
EgoTrainV1 IO module update.md|L32-L38|配置 训练 磁盘 sampleserver worker batchfea cached*dailyio_num_on_worker 允许 缓存 多天
EgoTrainV1 IO module update.md|L39-L43|磁盘 参数 worker ss remoteio batchfea queue passcontrol getbatchfea round
EgoTrainV1 IO module update.md|L44-L47|训练 磁盘 worker ss batchfea pass size barrier 固定 缓存
EgoTrainV1 IO module update.md|L48-L52|磁盘 sampleserver 任务 worker batchfea queue 请求 采用 最大 策略
EgoTrainV1 IO module update.md|L55-L74|参数 样本 batch_size minibatch dailyio batchfea shuffle ins queue batchparser
EgoTrainV1 IO module update.md|L85-L126|磁盘 worker ss daily parsed ins queue shuffle capacity shuffle_window_size
Enabling cpplint checks in Visual Studio Code \_VSCode*.md|L1-L4|install cpplint ensure installed system via pip already
Enabling cpplint checks in Visual Studio Code _VSCode_.md|L5-L8|mig ss install necessary extensions vscode extension microsoft haven installed
Enabling cpplint checks in Visual Studio Code _VSCode_.md|L9-L21|ss configure linter installing necessary extensions settings use cpplint files
Feature Dump.md|L1-L8|predictor 模型 训练 推理 样本 日志 特征 feature 耗时 rank
Feature Dump.md|L9-L26|ps 配置 推理 feature response protobuf git garena recommend srec*protos
Feature Dump.md|L29-L54|ps 淘汰 特征 带宽 内存 qps dump local cache ttl
Feature Dump.md|L57-L63|dumprequest dumpresponse service 接口定义
Feature Importance Evaluation.md|L3-L10|eval feature backgrounds importance evaluation model inspection technique used remove
Feature Importance Evaluation.md|L11-L17|slot sparse add_sparse_mask self slots list int categories none mask_type
Feature Importance Evaluation.md|L18-L24|dense feature add_dense_mask self block_name str masks list tuple int
Feature Importance Evaluation.md|L25-L33|feature masktype there mask types zero set all masked input
Feature admission and evict module.md|L8-L18|emb feature entry-criteria stage-2 creation mf segment other segments active_on_feature_creation
Feature admission and evict module.md|L21-L25|evict emb embedding feature decay previous step key role reduce
Feature admission and evict module.md|L26-L29|evict emb eviction feature decay program each key computed those
GOP跑模型优化的结果解析.md|L1-L81|模型 吞吐 ss record json pass step category normal plugin
GOP跑模型优化的结果解析.md|L82-L86|onnx opt_validation_status baseline pb vs optimized opted validate twist bad
GOP跑模型优化的结果解析.md|L87-L90|trt onnx onnx_trt_validation_status baseline graph_final vs optimized engine opted_graph_final batch
GOP跑模型优化的结果解析.md|L91-L93|trt trt_trt_validation_status baseline engine graph_final batch vs optimized opted_graph_final 对比
GPU benchmark 1_6_0.md|L1-L19|模型 训练 cpu 任务 ego-train worker a100 gpu 资源 耗时
GPU benchmark 1_7_0.md|L1-L19|模型 训练 cpu 任务 ego-train worker a100 gpu 资源 耗时
GPU benchmark.md|L1-L19|模型 训练 cpu 任务 ego-train worker a100 gpu 资源 ss
GPU pooling * dense allreduce与worker pooling性能对比测试*deprecated*.md|L5-L10|配置 训练 cpu 任务 a30 gpu 内存 soc tb pod
GPU pooling _ dense allreduce与worker pooling性能对比测试\_deprecated_.md|L11-L22|ps 训练 cpu 任务 a30 worker gpu checkpoint 内存 ss
GPU pooling _ dense allreduce与worker pooling性能对比测试\_deprecated_.md|L23-L28|训练 cpu gpu ss c3v3 机器 速度 置换 计算方法 时长
GPU pooling _ dense allreduce与worker pooling性能对比测试\_deprecated_.md|L31-L44|portal 模型 ps 训练 emb batch*size ego-portal feature hdfs cart_feat_unify_v4_hinet_v2_emb_new22_t_1_br
GPU pooling * dense allreduce与worker pooling性能对比测试*deprecated*.md|L45-L52|ps 训练 cpu 任务 gpu 内存 gb min 成本 对比
GPU pooling _ dense allreduce与worker pooling性能对比测试\_deprecated_.md|L53-L58|训练 cpu a30 gpu c3v3 min 速度 置换 比卡约
GPU pooling _ dense allreduce与worker pooling性能对比测试\_deprecated_.md|L59-L70|portal 模型 ps batch*size benchmark ego-portal hdfs dd_din_lt_esmm_mpi_softsim_2k_cl_adf_mgdcn_v2_br live-test model
GPU pooling * dense allreduce与worker pooling性能对比测试*deprecated*.md|L71-L78|ps 训练 cpu 任务 gpu 内存 gb min 成本 对比
GPU pooling _ dense allreduce与worker pooling性能对比测试\_deprecated_.md|L79-L84|训练 cpu a30 gpu c3v3 min 速度 置换 比卡约
GPU pooling _ dense allreduce与worker pooling性能对比测试\_deprecated_.md|L85-L98|portal 模型 ps batch*size ego-portal hdfs dsrm4_v5_ctr_prun_nn_t_5_l5 model model_management dsrm4_v5
GPU pooling * dense allreduce与worker pooling性能对比测试*deprecated*.md|L99-L106|ps 训练 cpu 任务 gpu 内存 gb min 成本 对比
GPU pooling _ dense allreduce与worker pooling性能对比测试\_deprecated_.md|L107-L111|训练 cpu a30 gpu c3v3 min 速度 置换 比卡约
GPU ss pooling与CPU worker pooling性能对比测试.md|L3-L8|mig 配置 训练 cpu 任务 a30 gpu 内存 soc tb
GPU ss pooling与CPU worker pooling性能对比测试.md|L9-L20|ps 训练 cpu 任务 a30 worker gpu checkpoint 内存 ss
GPU ss pooling与CPU worker pooling性能对比测试.md|L21-L26|训练 cpu gpu ss c3v3 机器 速度 置换 计算方法 时长
GPU ss pooling与CPU worker pooling性能对比测试.md|L29-L34|deepctr cpu 任务 ego-train batch*size worker gpu 资源 ss train
GPU ss pooling与CPU worker pooling性能对比测试.md|L35-L42|ps 训练 cpu 任务 gpu 内存 gb 成本 对比 占用
GPU ss pooling与CPU worker pooling性能对比测试.md|L43-L48|训练 a30 c3v3 速度 置换 比卡约
GPU ss pooling与CPU worker pooling性能对比测试.md|L49-L54|cpu 任务 ego-train batch_size worker gpu 资源 ss din train
GPU ss pooling与CPU worker pooling性能对比测试.md|L55-L62|ps 训练 cpu 任务 gpu 内存 gb min 成本 对比
GPU ss pooling与CPU worker pooling性能对比测试.md|L63-L68|训练 a30 c3v3 min 速度 置换 比卡约
GPU ss pooling与CPU worker pooling性能对比测试.md|L69-L74|cpu sparse 任务 ego-train batch_size worker gpu 资源 ss sparse_dnn_adf
GPU ss pooling与CPU worker pooling性能对比测试.md|L75-L82|ps 训练 cpu 任务 gpu 内存 gb 成本 对比 占用
GPU ss pooling与CPU worker pooling性能对比测试.md|L83-L88|训练 a30 c3v3 速度 置换 比卡约
GPU ss pooling与CPU worker pooling性能对比测试.md|L89-L94|cpu 任务 ego-train batch_size worker gpu 资源 ss dd_din_lt_mpi4_ge_id_light_gate train
GPU ss pooling与CPU worker pooling性能对比测试.md|L95-L102|ps 训练 cpu 任务 gpu 内存 gb 成本 对比 占用
GPU ss pooling与CPU worker pooling性能对比测试.md|L103-L108|训练 a30 c3v3 速度 置换 比卡约
GPU ss pooling与CPU worker pooling性能对比测试.md|L109-L114|cpu 任务 ego-train batch_size worker gpu 资源 ss search-ranking-deep-cvr train
GPU ss pooling与CPU worker pooling性能对比测试.md|L115-L122|ps 训练 cpu 任务 gpu 内存 gb 成本 对比 占用
GPU ss pooling与CPU worker pooling性能对比测试.md|L123-L128|训练 a30 c3v3 速度 置换 比卡约
GPU ss pooling与CPU worker pooling性能对比测试.md|L129-L134|cpu 任务 ego-train batch_size worker gpu 资源 ss dsrm_v3_2-2023080108 train
GPU ss pooling与CPU worker pooling性能对比测试.md|L135-L142|ps 训练 cpu 任务 gpu 内存 gb 成本 对比 占用
GPU ss pooling与CPU worker pooling性能对比测试.md|L143-L148|训练 a30 c3v3 速度 置换 比卡约
GPU ss pooling与CPU worker pooling性能对比测试.md|L149-L153|portal 模型 ps sparse ego-portal sparse_dnn_adf job url live-test training
GPU任务调优指南.md|L14-L20|max_context_per_device train_threads 训练 参数 显存 任务 max_session_per_device gpu ss tf_session_run
GPU任务调优指南.md|L23-L38|数据供给 round0 监控 配置 训练 converter worker minibatch 资源 ss
GPU任务调优指南.md|L39-L54|ps 训练 cpu 磁盘 任务 日志 worker gpu round total
GPU任务调优指南.md|L55-L90|max_context_per_device train_threads 监控 配置 训练 train_config worker gpu ss 耗时
GPU优化.md|L3-L13|ps trt release gpu gpuvideo-ads utilization comparison between release-2026-02-12-gpu green
GR模型Debug sparse input.md|L3-L18|feature hdfs ego debug client r2 projects rcmd_feature user shuquan
GR模型Debug sparse input.md|L19-L30|predictor ps sparse ss soc project service stateless-service detail tab
Go client.md|L7-L14|ego-predictor predictor ps zk client ego git garena ego-predictor-client-go tree
Go client.md|L15-L24|ego-predictor predictor 模型 ps 显存 部署 gpu 资源 负载均衡 client
Go client.md|L25-L29|ps ss 耗时 client server rpc p90 us avg grpc
Go client.md|L30-L35|rpc_dump rpc replay tool dump ego refer && 直接 集群
Go client.md|L36-L46|ps 调优 延迟 吞吐 耗时 grpc-go-client client grpc endpoint connection
Guardian User Manual.md|L1-L9|predictor guardian gpu ss debug ram recommend service appid appmodelname
Guardian User Manual.md|L10-L28|ego-predictor predictor 模型 ps 发布 cpu guardian publish subset client
Guardian User Manual.md|L29-L38|ego-predictor predictor 模型 ps 发布 serving guardian s3 git garena
Guardian User Manual.md|L44-L60|模型 serving guardian 显存 release gpu 资源 s3 ego-online-serving recommendation
Guardian User Manual.md|L61-L69|编译 predictor 模型 ps response git garena shuquan huang ego-client-test
Guardian User Manual.md|L80-L85|predictor 日志 response warning brpc server up replay bin ego_predictor_client
Guardian User Manual.md|L90-L93|monitoring predictor ps 监控 guardian grafana egopredictor infra sz rqcfeq64k
Guardian User Manual.md|L94-L104|模型 发布 guardian worker lyra pod flags cluster meta pause_align_lyra
Guardian User Manual.md|L105-L117|monitoring wc ego-predictor predictor ps grafana etcd infra sz sthmwcoza
Guardian User Manual.md|L118-L247|ps 发布 配置 guardian lyra guardian_server_name zfs services ai-platform-guardian-live-sg up
Guideline* measure model training speed among different backends in local.md|L5-L16|eval minibatch prepare data measurements launch train task training export
Guideline* measure model training speed among different backends in local.md|L17-L24|converter download all runtime files exported data ego-config pb graph
Guideline* measure model training speed among different backends in local.md|L33-L41|benchmark execute tool config*files_dir dir config files run_round_idx remains same
Guidelines of applying half precision optimization.md|L7-L15|eval ps half_precision sparse ss utilize offline training there three
Guidelines of applying half precision optimization.md|L16-L19|portal ps half_precision publish checkpoint utilize online inference egoportal publish_model
Guidelines of applying half precision optimization.md|L20-L26|eval ps attention want ensure prediction scores consistent between offline
Guidelines of applying half precision optimization.md|L29-L37|portal ps half_precision ego-learner utilize offline training only ps_half_precision still
Guidelines of applying half precision optimization.md|L38-L43|predictor half_precision checkpoint egopredictor utilize online inference generally want deploy
Guidelines of applying half precision optimization.md|L44-L47|eval ps half_precision attention ps_half_precision true predict scores between offline
Guidelines of using EGO Plugin V1.md|L13-L18|converter ss add data data-reading pipeline training samples processed defined
Guidelines of using EGO Plugin V1.md|L19-L50|ps converter hdfs apply built-in data currently there three converters
Guidelines of using EGO Plugin V1.md|L51-L55|predictor ps serving ss tips online upload both ego-plugin-online yaml
Guidelines of using EGO Plugin V1.md|L56-L80|converter implement new user-defined data yourself own meet customised demands
Guidelines of using EGO Plugin V1.md|L81-L85|sparse feature ss adjust labels weights drop out useless keys
Guidelines of using EGO Plugin V1.md|L86-L89|ego-plugin-v1 project times users may unique requirements incorporating specific operations
Guidelines of using EGO Plugin V1.md|L90-L137|sampleserver worker ss plugin functions role sample server read training
Guidelines of using EGO Plugin V1.md|L138-L188|sampleserver worker ss plugin functions responsible conducting model training receiving
Guidelines of using EGO Plugin V1.md|L189-L219|wc sampleserver worker coordinator ss plugin functions workercoordinator center unique
Guidelines of using EGO Plugin V1.md|L220-L225|ps emb sampleserver embedding sparse ss example egoplugin clustering learning
Guidelines of using Ego Plugin_Depreciated*.md|L1-L4|ss introduction during training ego support use user-defined shared library
Guidelines of using Ego Plugin*Depreciated*.md|L5-L18|train*config ego-learner step use ego plugin specify lib path yaml
Guidelines of using Ego Plugin_Depreciated*.md|L19-L44|ego-train step customize ego plugin start docker following instruction sudo
Guidelines of using Ego Plugin*Depreciated*.md|L45-L53|predictor ps serving tips online config plugin export online*export_config ego_plugin_path
H100 worker * ps混布性能测试草稿.md|L1-L10|h100 模型 训练 cpu 显存 样本 batch*size gpu dense 内存
H100 worker * ps混布性能测试草稿.md|L11-L31|round0 max*context_per_device train_threads ps round1 配置 训练 emb cpu 参数
H100多卡 * worker*ps混布性能测试.md|L1-L10|h100 模型 训练 cpu 显存 样本 batch_size worker gpu dense
H100多卡 * worker*ps混布性能测试.md|L11-L14|round0 max_context_per_device train_threads ps round1 配置 训练 emb cpu 参数
H100多卡 * worker*ps混布性能测试.md|L15-L18|round0 max_context_per_device train_threads ps round1 配置 训练 cpu 参数 显存
Handover.md|L1-L5|portal ps ego-portal test login uat live-test live 项目 地址
Handover.md|L6-L9|ps git garena aip fe ego-web 仓库 地址
Handover.md|L10-L13|portal ps ego-portal live-test api swagger index 接口 文档
Handover.md|L14-L19|上线 v02 产品 文档 进展 开始 开发
Handover.md|L20-L36|部署 yarn install dev mode uat build master test smc
How to Change_Add_Remove Optimizers During Loading Checkpoint.md|L1-L19|slot checkpoint change existing optimizers those want try another optimizer
How to Change_Add_Remove Optimizers During Loading Checkpoint.md|L20-L62|ps checkpoint add remove optimizers some may want dynamically adf
How to Eval Tensor.md|L1-L10|eval feature backgrounds model relatively large consume computing storage resources
How to Eval Tensor.md|L13-L16|eval feature declare tensor want evaluate model definition any only
How to Eval Tensor.md|L21-L24|ss hdfs checkout result dump file droprate each tensor output
How to Eval Tensor.md|L25-L27|ss additional dropout rate less than greater reduce loss_coefficient
How to Evaluate Feature Importance.md|L5-L17|eval feature step evaluate importance set masking model definition please
How to Freeze Graph to compare diff.md|L1-L4|upload new model python script above
How to Freeze Graph to compare diff.md|L5-L21|portal eval ps ego-portal checkpoint online evaluation round run using
How to Freeze Graph to compare diff.md|L22-L30|portal deepctr ps serving ego-portal online reference batchmodelserving deepctr_online_serving detail
How to clip or map nn parameters.md|L1-L10|clipping nn model layers don want load certain parameters filter
How to clip or map nn parameters.md|L11-L26|feature mapping nn model layers configure follows both offset length
How to clip or map nn parameters.md|L27-L32|feature greedy load set true only layers matching names shapes
How to clip or map nn parameters.md|L33-L36|feature load optimizer set false only parameters loaded default value
How to clip or map nn parameters.md|L37-L48|checkpoint ss load nn multiple checkpoints read parameters them current
How to clip or map nn parameters.md|L49-L54|ss more greedy load all same-name tensor including same-shape different-shape
How to clip or map nn parameters.md|L55-L94|ps feature hdfs edit model python above features meet needs
How to clip or map nn parameters.md|L95-L125|portal ps worker checkpoint why my job failed loading because
How to compile model manually.md|L1-L16|portal ps ego-train compile ego-portal company server find suitable docker
How to compile model manually.md|L17-L37|ps compile own macbook don recommend way want facilitate follow
How to config online-export task_generate validate samples*.md|L1-L7|feature paste origin validate samples optional expect add prepare collection
How to create a model & version*.md|L1-L22|feature register model version having use ui call create_model_version sh
How to create a model & version*.md|L23-L39|shell create*model_version sh model_id model_path entry_file model_version_name model_version_desc test create
How to define a list wise model.md|L1-L35|step config fixed list length case there no sufficient items
How to define a list wise model.md|L36-L48|sparse dense feature ss enable pageview compression mode pv compress
How to feed src_ids.md|L5-L10|slot sparse feature directly specify sample src_id example means key
How to feed src_ids.md|L11-L15|dense feature int64 means egograph read int64_my_src_id src_id please note
How to integrate with graph relations_EgoGraph*.md|L12-L17|slot sparse dense feature sampling refers querying adjacent nodes through
How to integrate with graph relations*EgoGraph*.md|L18-L23|slot dense feature ss updating update associate src*id multiple dst_id
How to integrate with graph relations_EgoGraph*.md|L24-L44|slot sparse dense feature register node info define sideinfo contain
How to integrate with graph relations*EgoGraph*.md|L45-L47|launch job switch needs turned submitting task
How to modify the serving graph.md|L1-L14|ckpt 发布 serving release feature ss applicable scenarios suitable following
How to modify the serving graph.md|L15-L20|ckpt 发布 serving compile feature overview ego supports uploading online
How to modify the serving graph.md|L21-L37|ckpt 发布 serving compile instructions creating model-version model- version define
How to modify the serving graph.md|L38-L42|compile demo online*compile_config json model py
How to publish models to ego-predictor.md|L9-L14|publish checkpoint publishing well-trained model those four files above figure
How to release models to ego-predictor*.md|L7-L12|release checkpoint ss well-trained model finished training access list corresponding
How to release models to ego-predictor*.md|L13-L32|ps publish checkpoint shell push_model_to_online_ps sh model_id model_version_id checkpoint_id online_model_name
How to submit a training job.md|L6-L11|ps register model having those three files illustrated above call
How to submit a training job.md|L12-L17|ps register model version having call create_model_version sh scheduling scripts
How to submit a training job.md|L18-L28|ps submit training job having model version now there re
How to submit a training job*.md|L7-L26|compile submit batch training job select new go form there
How to submit a training job*.md|L27-L55|ego_learner converter worker checkpoint sample_server shell launch_job sh job_name model_id
How to upgrade your model to tf2.md|L3-L15|apply tf upgrade tool model scripts find latest tf2 image
How to use cpp converter.md|L3-L6|converter references thanks summarizing his experience using cpp
How to use cpp converter.md|L7-L10|ps converter debug cpp converters validate conversion python through use
How to use cpp converter.md|L11-L28|converter ego-train ego-learner debug cpp converters get tool ego runtime
How to use cpp converter.md|L29-L32|converter release images there some converters whose official versions yet
How to use cpp converter.md|L33-L36|converter converts following introduce converters one
How to use cpp converter.md|L37-L54|ps ss luaextractor arguments lua_script_path users use lua customize function
How to use cpp converter.md|L55-L88|ps ss labelextractor arguments lua_script_path users use lua customize function
How to use cpp converter.md|L89-L112|ps ss multitaskextractor arguments lua_script_path users use lua customize function
How to use cpp converter.md|L113-L128|slot dense feature denseextractor arguments name consistent ego get_dense_feature slots
How to use cpp converter.md|L129-L152|ps dense denseextractorv2 arguments lua_script_path users use lua customize function
How to use cpp converter.md|L153-L164|slot sparse feature sparseextractor arguments kept_sparse_slots slots reserved excluded_sparse_slots removed
How to use cpp converter.md|L165-L174|dense feature ss stablecheck arguments bound upper lower limits description
How to use cpp converter.md|L175-L188|converter filterbytimestamp please note using requires data contains timestamp parquet
How to use cpp converter.md|L189-L202|ps filterbydebuginfo arguments lua_script_path users use lua customize filter function
How to use cpp converter.md|L203-L216|ps filterbyactioninfoanddebuginfo arguments lua_script_path users use lua customize filter function
How to use cpp converter.md|L217-L230|ps dense feature adfdensefeature arguments lua_script_path users use lua customize
How to use cpp converter.md|L231-L244|ps filterbysampleid arguments lua_script_path users use lua customize filter function
How to use cpp converter.md|L245-L258|ps extractuseridfromsampleid arguments lua_script_path users use lua customize filter function
How to use cpp converter.md|L259-L276|ps dense denseextractorfromdebuginfo arguments lua_script_path users use lua customize filter
How to use cpp converter.md|L277-L294|ps dense denseextractorfromsampleid arguments lua_script_path users use lua customize function
How to use cpp converter.md|L295-L311|ps extractrequestidfromsampleid arguments lua_script_path users use lua customize filter function
How to use cpp converter.md|L312-L325|ps feature extractoriginfeaturefromdebuginfo arguments lua_script_path users use lua customize filter
How to use cpp converter.md|L326-L339|labelmapping arguments dict_path path custom dictionary stored rows using key-value
How to use cpp converter.md|L340-L357|ps extractint64feat arguments lua_script_path users use lua customize filter function
How to use cpp converter.md|L358-L393|dense negativesample arguments sample_window_size number users requests negative sampling window
How to use cpp converter.md|L394-L415|slot sparse dense feature getsparsefeaturekeys arguments key expected dense_feature_name name
How to use cpp converter.md|L416-L429|slot sparse dense feature convertfeaturedensetosparse arguments key placed hash_slot hash
How to use cpp converter.md|L430-L455|wc converter showclickextractor note bug version image use page labelextractor
How to use cpp converter.md|L456-L473|slot slotmapping v1 arguments dst_slot new copied src_slot hash_slot hash
How to use cpp converter.md|L474-L499|slot slotmappingbyscenario v1 arguments dst_slot new copied src_slot hash_slot hash
How to use cpp converter.md|L500-L513|ps filterbysampleidanddebuginfo v1 arguments lua_script_path users use lua customize filter
How to use cpp converter.md|L514-L527|ps filterbyactioninfoandsampleidanddebuginfo v1 arguments lua_script_path users use lua customize filter
How to use cpp converter.md|L528-L555|ps filterbysome v1 arguments lua_script_path users use lua customize filter
How to use cpp converter.md|L556-L567|feature replacefeaturekey v1 arguments old key search new replace value
How to use cpp converter.md|L568-L581|dense feature constdensefeature v1 arguments name consistent ego get_dense_feature value
How to use cpp converter.md|L582-L599|ss mergebyrequestid v1 arguments key_request_id key request_id sample default min
How to use cpp converter.md|L600-L638|mergebyrequestidcustom v1 arguments key_request_id key request_id sample default lua_script_path users
How to use cpp converter.md|L639-L644|feature deduplicationcommonfeature v1 description remove duplicate user features request generally
How to use cpp converter.md|L645-L666|ps extensioninfo v1 arguments lua_script_path users use lua customize extract
How to use cpp converter.md|L667-L684|dense denseextractorfromitemattribute v1 arguments lua_script_path users use lua customize extract
How to use cpp converter.md|L685-L702|slot dense denseslotmappping v1 arguments dst_slot new converted src_slot lua_func
How to use cpp converter.md|L703-L728|slot dense denseslotmapppingbyscenario v1 arguments dst_slot new converted src_slot lua_func
How to use cpp converter.md|L729-L750|negativesamplenoncontinuoususer v1 arguments sample_window_size number positive sample negative sampling window
How to use cpp converter.md|L751-L764|slot sparse feature modsparsefeatures v1 arguments modulo number slots mod
How to use cpp converter.md|L765-L782|slot sparse sparseslotfilterbyscenario v1 arguments kept_sparse_slots slots reserved excluded_sparse_slots removed
How to use cpp converter.md|L783-L796|slot dense feature countoccurrencesinsequence v1 arguments dense_feature_name name used store
How to use cpp converter.md|L797-L810|coloringlabelinrequest v1 arguments src_label_idx index conditional label dst_label_idx modified dst_weight
How to use cpp converter.md|L811-L818|converter ifclickrequest v1 description there positive sample click request all
How to use cpp converter.md|L819-L824|aggregationsampleid v1 description merge sampleid debuginfo actionmap usually dump tensor
How to use cpp converter.md|L825-L830|countactioninrequest v1 description count action request put result extension info
How to use cpp converter.md|L831-L850|replacesampleid v1 arguments lua_script_path users use lua customize function new
How to use cpp converter.md|L851-L874|duplicatesample v1 arguments lua_script_path users use lua customize function generating
How to use cpp converter.md|L875-L896|sparse feature ss sparsereassign v1 arguments lua_script_path users use lua
How to use cpp converter.md|L897-L920|sparse feature ss sparseextractorv2 v1 arguments lua_script_path users use lua
How to use cpp converter.md|L921-L939|sparse publish dense feature ss tagmergedensefeature published yet arguments lua_script_path
How to use i-Razor for feature selection and slot dimension search.md|L1-L18|slot feature background i-razor used selection specifying appropriate dimensions conventional
How to use i-Razor for feature selection and slot dimension search.md|L19-L78|slot integration ego pretrain provides two apis use i-razor seq_irazor_slot
How to use streaming vq.md|L1-L8|ps 发布 background streamingvq streaming vector quantization vq real-time indexing
How to use streaming vq.md|L11-L14|api tf2 tf1 支持 时请 镜像
How to use streaming vq.md|L15-L35|emb 参数 样本 embedding 任务 item item_id uint64_t cluster item_bias
How to use streaming vq.md|L36-L41|portal 配置 cpu 参数 vq memory 开启 服务
How to use streaming vq.md|L44-L76|模型 配置 kafka ego-learner checkpoint ss yaml cluster_name vq codebook
How to use streaming vq.md|L79-L86|监控 cluster item empty sum avg p90 p99 分布 表示
How to use streaming vq.md|L87-L90|模型 item cluster 迁移 指标 用来 判断 稳定性 不停 另外
How to use streaming vq.md|L91-L100|日志 worker checkpoint hdfs 数据格式 grep vq_cluster cc shard vq
Hyperparameter Tuning in EGO with NNI.md|L5-L10|ss installation guide fetch source code upgrade latest toolchain install
Hyperparameter Tuning in EGO with NNI.md|L11-L24|portal deepctr eval define search space import hyperparameters example going
Hyperparameter Tuning in EGO with NNI.md|L25-L34|ss creating experiment create training service config follows modify necessary
Hyperparameter Tuning in EGO with NNI.md|L35-L51|ss running experiment start nni ui should available unless specified
L4 V100 T4 A30卡代表模型吞吐性能对比.md|L1-L14|模型 l4 cpu a30 gpu t4 summary v100 g8v2 g1v2
L4 V100 T4 A30卡代表模型吞吐性能对比.md|L15-L29|模型 ps l4 emb cpu 推理 a30 特征 gpu 资源
L4 在线服务测试.md|L1-L4|l4 a30 gpu t4 summary s1v2 mark gpucart gpuddmy video2
L4 在线服务测试.md|L5-L12|l4 配置 cpu 延迟 a30 gpu 吞吐 gpucart livesg10v2 cores
L4 在线服务测试.md|L13-L16|l4 配置 cpu 延迟 a30 gpu 吞吐 gpuddmy g10v2 cores
L4 在线服务测试.md|L17-L22|l4 配置 cpu 延迟 gpu 吞吐 t4 gpuvideo g10v2 cores
L4 在线服务测试.md|L23-L51|l4 配置 cpu 延迟 gpu 吞吐 video2 g10v2 cores latency
L4 在线服务测试.md|L52-L106|l4 配置 cpu 延迟 a30 gpu 吞吐 video5 g10v2 cores
L4 在线服务测试.md|L107-L110|l4 配置 cpu 延迟 gpu 吞吐 t4 livestream g10v2 cores
L4 在线服务测试.md|L111-L126|模型 l4 配置 cpu 延迟 gpu 吞吐 livestream2 g10v2 cores
L4 在线服务测试.md|L127-L130|l4 配置 cpu 延迟 a30 gpu 吞吐 search g10v2 cores
L4 在线服务测试.md|L131-L183|l4 配置 cpu 延迟 gpu 吞吐 video5 dynamic g10v2 cores
L4 在线服务测试.md|L184-L189|l4 配置 cpu 延迟 gpu 吞吐 pdp-ads g10v6 cores latency
L4 在线服务测试.md|L190-L197|l4 配置 cpu 延迟 gpu 吞吐 t4 pdp-organic g10v6 cores
L4 在线服务测试.md|L198-L202|l4 配置 cpu 延迟 gpu 吞吐 t4 search-gpusguide-dynamic g10v6 cores
Local Debug.md|L14-L18|batch_size minibatch feature hdfs dump input gradient file set enable_dump_batch
Local Debug.md|L19-L25|batch_size minibatch print tensorflow layer log set enable_tf_print true configure
Local Debug.md|L26-L29|ego-learner submit job adding local debug configs yaml training controller
Manual Downgrade.md|L8-L27|truncate item count condition flags_open_itemcount_downgrade true req items_size flags_downgrade_max_itemcount mark
Manual Downgrade.md|L28-L33|ss drop percent request modify python script set gflag requests
Metric sub groups.md|L15-L17|converter dense feature ss features currently used bool expresssions support
MetricControl改造方案.md|L1-L8|wc 训练 任务 worker 内存 耗时 converttometricbatch metric_batches round metriccontrol
MetricControl改造方案.md|L9-L17|同步 metric addbatch preparecalc beginround schedulethreadpool metric_batches calc groupauc alltoall
MetricControl模块现状梳理和未来优化讨论.md|L1-L6|训练 样本 耗时 metriccontrol calc 当前 现状 上图 展示 模块
MetricControl模块现状梳理和未来优化讨论.md|L7-L26|rmse auc gauc addbatch calc 简单 回顾 一下 计算 流程
MetricControl模块现状梳理和未来优化讨论.md|L27-L32|wc 模型 训练 worker metric gauc auc rmse chief target
MetricControl模块现状梳理和未来优化讨论.md|L33-L42|wc 模型 训练 worker mpi tag communicationgroup metrics clients metric
Migrating from Python to Cpp Converter.md|L8-L11|ads files read up deeply each individual function converts please
Migrating from Python to Cpp Converter.md|L12-L19|参数 样本 filterbysome python config debug_info action_map true lua use_action_info
Migrating from Python to Cpp Converter.md|L20-L27|配置 dense feature denseextractorbydebuginfo python config debug_info lua func name
Migrating from Python to Cpp Converter.md|L28-L35|wc showclickextractor python config is_show label direct_label_7d show click use_debug_info
Migrating from Python to Cpp Converter.md|L36-L42|配置 参数 ego-learner multitaskextractor python config label weight multiextractor extra_params
Migration from CPU to GPU Training.md|L4-L14|max_context_per_device train_threads gpu ss oom basic configurations training suggest use
Migration from CPU to GPU Training.md|L15-L21|cpu a30 gpu enable mixed training enable_gpu_cpu_mixed_training many pod cores
Migration from CPU to GPU Training.md|L22-L26|max_context_per_device max_session_per_device gpu ss oom reduce memory consumption gpu_merge_batch_buffer_size suggest
Model Performance Metrics.md|L101-L109|ego-learner ss yaml metric config min_num_samples_in_group number samples user less
Model Performance Metrics.md|L110-L112|ps ego-learner ss sub group picked user including yaml file
Monitor Cleanup.md|L1-L12|ss problematic panels fixed done usage memory quota sample_num change
Monitor Cleanup.md|L13-L27|sampleserver ss unused panels removed resource usage max_concurrent_sess_run count invalid_files_num
Monitor Cleanup.md|L28-L34|mig worker ss hdfs metrics transfer remove their respective monitors
Multi-hop sampling.md|L1-L12|slot feature multi-hop sampling refers taking dst_ids previous src_ids next
Multi-hop sampling.md|L13-L19|batch_size get number dst_ids multi-hop sampling may want know relationship
Multihash_Q-R* and Binary code based hash experiment.md|L3-L4|portal deepctr 模型 ps evict 训练 准入 ego-portal experiment settings
NSC*Negative Sample Center* user manual.md|L17-L22|sparse converter dense feature txt format py category item*id should
NSC_Negative Sample Center* user manual.md|L23-L28|protobuf format case user should add item*id category ext field
NSC_Negative Sample Center* user manual.md|L31-L34|checkpoint save timing root path nsc cache operation same those
NSC*Negative Sample Center* user manual.md|L35-L39|checkpoint load default nsc cache go load*model_path try however some
NSC_Negative Sample Center* user manual.md|L40-L45|generate negative samples nsc recording trained sample training click*count greater
NSC_Negative Sample Center* user manual.md|L46-L55|ss sampling weight nsc supports now calculation formula click*count click_power
NSC_Negative Sample Center* user manual.md|L56-L62|ego-learner feature yaml config file users specify many nsc-related configurations
New EGO User Manual Index.md|L9-L12|through basic introduction know ego services provide why should use
New EGO User Manual Index.md|L13-L16|quickly understand some basic concepts ego help better learn use
New EGO User Manual Index.md|L19-L24|portal ps ss access process ego quick start business just
New EGO User Manual Index.md|L27-L30|generally introduce structures ego expect give picture
New EGO User Manual Index.md|L31-L34|publish ss chapter teach lesson overall pipeline training publishing
New EGO User Manual Index.md|L37-L40|portal ps ego user manual bego ve read three chapters
New EGO User Manual Index.md|L41-L44|here use ego api through scripts
New EGO User Manual Index.md|L45-L50|debug yourself following way
New EGO User Manual Index.md|L135-L140|ps ego sample src contextnavpagetreemode support native parquet format three
New EGO User Manual Index.md|L141-L155|egotrain ps slot emb ss extensions src contextnavpagetreemode cache tensor
New EGO User Manual Index.md|L156-L168|ps evict slot emb embedding sparse feature ss admission module
New EGO User Manual Index.md|L189-L192|predictor egopredictor trained good model start use inference
New EGO User Manual Index.md|L227-L238|ss ask help ego service system-- three-stage rocket fast-pass training
News* openmpi-4_1_0_tgz-1_0_2-202107261530.md|L7-L17|eval slot sparse ego-learner dense feature p1 yaml train_mode evalfea
News* openmpi-4*1_0_tgz-1_0_2-202107261530.md|L18-L26|slot emb ego-learner dense p2 yaml add load_slots could shows
News* openmpi-4*1_0_tgz-1_0_2-202107261530.md|L27-L33|slot p3 dnn-plugin yaml add mf_slots_pooling_methods pooling_types shows pooling would
News* openmpi-4*1_0_tgz-1_0_2-202107261530.md|L34-L37|ss p4 end each pass day ego would many legal
News* openmpi-4*1_0_tgz-1_0_2-202107261530.md|L38-L42|p5 example debug want export output each layer set is_layer_res_output
News* openmpi-4*1_0_tgz-1_0_3-202108031400.md|L4-L9|ego-learner p1 yaml open gauc output adding is_gauc_output true round
News* openmpi-4*1_0_tgz-1_0_3-202108031400.md|L10-L14|p2 firstly setting up is_layer_res_output true round layer_res_path layer_res_days offline_runner
Normalization.md|L1-L20|ps ego normalization name momentum epsilon e-6 trainable true considered
OfflineRound.md|L9-L22|ps sparse dense ss hdfs offlineround name targets final_loss train_sparse
Offloading Push Quantization to the PS Client.md|L21-L57|模型 ps server push float32 half bhalf pushrequest pt update_value
Offloading Push Quantization to the PS Client.md|L58-L76|模型 ps 上线 client push mix int8 server payload pstool
Online Learning NN参数更新加速.md|L15-L18|ps nn update api docs google document qihljxy7zipeqeoopz7qcrqnadoizcyyguhscar_hbs edit tab
Online Learning优化设计.md|L12-L25|ckpt ps 任务 资源 training stop train job offline dump
Online Learning优化设计.md|L26-L53|online_learning 配置 serving 参数 bug nn update online_model frozen online
Online Learning优化设计.md|L54-L83|ps 同步 参数 淘汰 任务 release nn fkeys sub job
Online Learning优化设计.md|L84-L95|监控 配置 serving 同步 告警 release online model train job
Online Learning优化设计.md|L96-L104|模型 训练 同步 kafka checkpoint ab train job online learning
Online Learning优化设计.md|L105-L107|ckpt serving kafka 告警 资源 owner training ol train job
Online Learning优化设计.md|L108-L110|ps online learning docs google document h7r5slivcse5fpvp6bxzmt2p1epb4fyz-\_0ywkl_ts edit tab 参考
Online PS SG10 * SG9 服务混部.md|L7-L22|ps onlineps 部署 资源 dr docs google spreadsheets kihibzktdxm-ozhdpqoy1wkhlx1u33onposyu0c3x0u edit
Online PS SG10 _ SG9 服务混部.md|L23-L30|部署 sg c3v2 混合 方案 我们 希望 同一个 集群 不同
Online PS SG10 _ SG9 服务混部.md|L31-L45|ps onlineps onlineps-common*sg10 onlineps-common_sg7 onlineps-recommendation-test onlineps-search-guide sg onlineps-hawkinga onlineps-recommendationb onlineps-recommendationg
Online PS SG10 * SG9 服务混部.md|L46-L95|ps onlineps sg onlineps-recommendation-test onlineps-tests dr onlineps-recommendationc onlineps-recommendationg c3v2 c3v3
Online issues.md|L1-L12|coredump ss template report issue new model yes differece old
Online issues.md|L13-L15|coredump predictor release ss issues record info reason log time
Online learning rebase peroid training.md|L5-L7|serving 任务 online learning train job 名词解释 同一个 多个 分散
Online learning rebase peroid training.md|L8-L90|serving release period training job online learning train createjobhandler rebase
Online learning rebase peroid training.md|L91-L96|online*learning train job online learning ec_online_model_tab online_learning_id 历史数据 迁移 存量
Online learning rebase peroid training.md|L101-L105|portal prd ps period training online learning docs google document
OnlineRound.md|L6-L14|onlineround name targets param used round return value example
Only Update Assign Slots in a Round.md|L1-L5|serving slot emb ss cache tensor assign slots speed up
Only Update Assign Slots in a Round.md|L6-L13|slot emb ss only update assign slots round config should
Optimize embedding.md|L3-L6|slot emb present flow mergeslot remove duplicate look up fill
Optimize embedding.md|L7-L10|emb feature optimize solution replace landing table absl flat_hash_map remove
Optimize embedding.md|L13-L24|cpu ss stress test server cores mem model dd_atc_order data
Optimize embedding.md|L25-L34|binding numa statistics data predictv3 pb items keys remove duplicate
Optimize embedding.md|L35-L39|slot emb embedding ss version fkeys should different between slots
Optimizer Modification Guide.md|L3-L58|emb embedding ss background consists several segments each corresponding optimizer
Optimizer Modification Guide.md|L59-L132|checkpoint feature ideal state target model editing capability goal use
Optimizer Modification Guide.md|L133-L137|模型 current implementation currently model editing supports change delete add
Optimizer Modification Guide.md|L138-L186|slot change modify optimizer prerequisite filter slots grads restrictions cannot
Optimizer Modification Guide.md|L187-L218|ps ss delete remove optimizer prerequisite greedy_load true restrictions cannot
Optimizer Modification Guide.md|L219-L262|ps slot ss add optimizer prerequisites greedy_load true grads_slot_ids list
Optimizer Modification Guide.md|L263-L281|slot general rules single only one type operation add delete
Optimizer.md|L5-L8|extend self-defined optimizer refer part under
Optimizer.md|L11-L14|ps dense config params default nn global optimizer defaultdenseoptimizer effect
Optimizer.md|L15-L18|ps specify optimizer one layer tensor set_layers_optimizer
Optimizer.md|L19-L22|emb modify optimizer please view learn some basic knowledges ego
Optimizer.md|L25-L28|ps sparse use defaultsparseoptimiser these two segments default refer config_lr
Optimizer.md|L29-L39|emb use other optimizer method1 config_lr_optimizer config_mf_optimizer api please refert
Optimizer.md|L40-L42|other segments extend specified optimizer
Optimizing Model Graph to Improve TensorRT Model Inference Speed* Practical Tips and Techniques.md|L1-L4|ps tensorrt overview documentation describes some practical tips techniques optimize
Optimizing Model Graph to Improve TensorRT Model Inference Speed* Practical Tips and Techniques.md|L7-L10|ps feature ss optimizing memory bound ops recommendation models usually
Optimizing Model Graph to Improve TensorRT Model Inference Speed* Practical Tips and Techniques.md|L11-L30|ps feature ss optimize concat op most recommendation models accepts
Optimizing Model Graph to Improve TensorRT Model Inference Speed* Practical Tips and Techniques.md|L31-L38|ps tensorrt optimize split unsqueeze concat pattern above inference graph
Optimizing Model Graph to Improve TensorRT Model Inference Speed* Practical Tips and Techniques.md|L39-L46|emb embedding ss optimize adf segment processing some cvr models
Optimizing Model Graph to Improve TensorRT Model Inference Speed* Practical Tips and Techniques.md|L49-L62|ps quantization once memory bound ops optimized usually matmul becomes
Optimizing Model Graph to Improve TensorRT Model Inference Speed* Practical Tips and Techniques.md|L63-L65|mig slot emb embedding intializer initializers might affect precisions well
PS Client load balancer.md|L1-L12|loadbalancer runtime load balancer lb0 lb1 lb2 metric server fetchrequestheader
PS Client load balancer.md|L13-L22|ps load balancer impl brpc lb rr psrr ban unban
PS Client load balancer.md|L23-L34|ps 跨机房 rr physical selector roundrobin naming client physical*cluster psroundrobinloadbalancer
PS Client load balancer.md|L39-L48|ps 延迟 跨机房 耗时 silver bullet brpc lalb locality-aware load
PS Model Load User Manual.md|L107-L116|portal sparse checkpoint feature job creation page ego controller new
PS Model Load User Manual.md|L117-L133|slot api example requesting controller create job mode above parameters
Perf SS Benchmark.md|L1-L12|wc cpu 内存 ss 耗时 c3v3 intel xeon platinum ghz
Perf SS Benchmark.md|L13-L14|模型 cpu 参数 样本 benchmark 内存 hdfs 耗时 dsrm_v5 r2
Perf SS Benchmark.md|L15-L17|模型 样本 耗时 s2v6 c3v3 测试 结论 上述 解析 基本
Period Training_Online Learning融合设计方案.md|L3-L7|ckpt 样本 ss online learning peroidruleid successed job jobid sample_data_timestamp
Period Training_Online Learning融合设计方案.md|L8-L12|online learning train job stop 更新 如何 停止 列表 提供
Period Training_Online Learning融合设计方案.md|L15-L19|ps api period training online learning docs google document p5xls4pbaqp5l6drbq4dhbmm6s3wlrviqkrkqlidoqg
PredictV3 for no fg request.md|L3-L27|模型 日志 ss request protocol message field type mark predictrequestv3
PredictV3 for no fg request.md|L28-L37|ss response proto message field type mark predictresponsev3 status_code statuscode
PredictV3 for no fg request.md|L38-L43|ss 耗时 debug debug_id request response debug_info server ip host_ip
Predictor management详细设计.md|L3-L7|portal prd predictor ps ego v0 egoportalv0 prd-3 e6 af
Profiling Tensorflow in EGO.md|L3-L6|enable tracing flags txt add two option launch job
Profiling Tensorflow in EGO.md|L7-L14|worker convert metadata chrome tracing format enter pod through terminal
Profiling Tensorflow in EGO.md|L15-L18|view timeline chrome browser open link tracing json file
Profiling Tensorflow in EGO.md|L21-L24|enable tracing flags txt add option launch job
Pytorch Activation Checkpointing.md|L7-L14|模型 检查点 checkpoint checkpoint_sequential def sequence_model segments input use_reentrant none
Pytorch Activation Checkpointing.md|L15-L27|检查点 checkpoint def function args use_reentrant optional bool none context_fn
Pytorch Metirc计算设计文档.md|L3-L11|训练 minibatch ss batch train_data metric_control- addbatch metric_batch target report
Pytorch Metirc计算设计文档.md|L12-L15|训练 优势 支持 指标 计算 流程 异步 多个 线程 并行执行
Pytorch Metirc计算设计文档.md|L16-L20|metric_control targetcontrol converttosampledata static converttotargetdata pytorch 代码 实现 复用 模块
RDMA performance survey.md|L7-L14|experiment settings conducted two physical machine each one memory connected
RDMA performance survey.md|L15-L20|ps cpu ss experiment results launched two process server send
RDMA performance survey.md|L21-L23|ps conclusion rdma help online increase qps optimize latency
RTX PRO 6000 Blackwell Server Edition.md|L3-L54|l40s 模型 ps l4 a30 dense summary rtx flops gr
Resource Usage Metrics.md|L7-L15|cpu ss usage used look utilisation cores aim make mean
Resource Usage Metrics.md|L16-L21|ss oom memory usage pod_request amount user requested pod compared
Resource Usage Metrics.md|L22-L27|gpu util shows utilisation rate out higher more efficient using
Resource Usage Metrics.md|L28-L33|gpu ss mem util shows memory utilisation rate out higher
Resource Usage Metrics.md|L34-L39|used memory quota ratio shows amount sample servers out would
Resource Usage Metrics.md|L42-L45|disk usage pod here used check much space being caching
Resource Usage Metrics.md|L46-L49|available disk cache ratio used check percentage space being caching
Resource Usage Metrics.md|L50-L55|mig worker disk gb pod useful would want check individual
Resource Usage Metrics.md|L56-L65|worker minibatch memory counter consists many different indicators look usage
Resource Usage Metrics.md|L66-L71|worker ss sample server memory counter similar consists amount bytes
Resource Usage Metrics.md|L72-L75|network mb used measure speed pods receive send data mainly
Resource Usage Metrics.md|L76-L80|mig gpu temperature degree celcius might useful spot bugs there
S1V2与C3机器置换比测试.md|L3-L4|ps cpu a30 gpu server config name s1_v2 c3 g18v3
S1V2与C3机器置换比测试.md|L7-L20|portal ps ego-portal dsrmv552 search rank c3 live-test training job
S1V2与C3机器置换比测试.md|L21-L33|portal ps ego-portal prerank_v6_1_dcn_v2_unified_full search rough rank c3 live-test training
S1V2与C3机器置换比测试.md|L36-L48|portal ps converter ego-portal dd_dm_sdm_rt_v3_esmm_price_id_pow_id python rcmd recall c3 live-test
S1V2与C3机器置换比测试.md|L49-L61|portal ps ego-portal ranking-pdp-25-8-60-pre-optim rcmd rough rank c3 live-test training
S1V2与C3机器置换比测试.md|L62-L75|portal ps ego-portal ss cross_scen_cvr_model3_v31_base2_id cr rcmd rank c3 live-test
S1V2与C3机器置换比测试.md|L76-L78|模型 内存 c3 s1v2 总结 基于 以上 测试 机型 置换
S1V2与C3机器置换比测试\_depreciated*.md|L3-L9|portal ps ego-portal dsrmv552 c3 live-test training job detail info
SS pooling cpu perf comparison.md|L1-L2|portal deepctr ps cpu worker ego-portal ss resource job link
SS优化*Search CTR*收益统计.md|L3-L8|样本 sampleserver 任务 ss ss*read_samples 测算 方式 维持 两个 指标
SS优化\_Search CTR*收益统计.md|L11-L20|portal ps ego-portal ss training periodrule detail info current pagesize
SS优化*Search CTR*收益统计.md|L21-L28|portal ps ego-portal ss training periodrule detail info current pagesize
SS优化*Search CTR*收益统计.md|L29-L38|portal ps ego-portal ss training periodrule detail info current pagesize
SS优化*Search CTR*收益统计.md|L39-L48|portal ps ego-portal ss training periodrule detail info current pagesize
SS优化*Search CTR*收益统计.md|L49-L60|portal ps ego-portal ss training periodrule detail info current pagesize
SS优化*Search CTR*收益统计.md|L61-L72|portal ps ego-portal ss training periodrule detail info current pagesize
SS优化*Search CTR*收益统计.md|L73-L84|portal ps ego-portal ss training periodrule detail info current pagesize
SS优化*Search CTR*收益统计.md|L85-L96|portal ps ego-portal ss training periodrule detail info current pagesize
SS优化*Search CTR*收益统计.md|L97-L108|portal ps ego-portal ss training periodrule detail info current pagesize
SS优化*Search CTR*收益统计.md|L109-L111|训练 sampleserver 任务 ss core 总结 针对 周期性 优化 镜像
SS优化*Search CVR收益统计.md|L3-L14|portal ps 训练 ego-portal ss training periodrule detail info current
SS优化\_Search CVR收益统计.md|L15-L26|portal ps 训练 ego-portal ss model model_management cvr_new_model_v3 version cvr_newbase_v31_dcn_gradcraft_stage3
SS优化\_Search CVR收益统计.md|L27-L36|portal ps 训练 ego-portal ss model model_management cvr_new_model_v3 version cvr_newbase_v31_dcn_gradcraft_stage5
SS优化*推荐CTR*CR*收益统计.md|L3-L18|portal ps ego-portal ss dd model model*management dd_rank_id_masknet_restart_ads_madltrpfc version v0
SS优化*推荐CTR*CR*收益统计.md|L19-L28|portal ps ego-portal ss pdp model model*management pdp_ctr_unclick_seq_t version swsh_hm2
SS优化*推荐CTR*CR*收益统计.md|L29-L36|portal ps ego-portal ss pp model model*management cart_unify_ads_org_mix version pc_cali
SS优化*推荐CTR*CR*收益统计.md|L37-L47|portal ps ego-portal ss cr model model*management cross_scen_cvr_model3_v31 version base2
SS优化*推荐混排*收益统计.md|L1-L8|portal ps ego-portal pdp training job detail info tab task
SS优化*推荐混排*收益统计.md|L9-L16|portal ps ego-portal pdp training job detail info tab task
SS优化*推荐混排*收益统计.md|L17-L28|portal ps ego-portal pmatch dd ph training job detail info
SS优化*推荐混排*收益统计.md|L29-L40|portal ps ego-portal pmatch dd training job detail info tab
SS优化*推荐混排*收益统计.md|L41-L50|portal ps ego-portal prank dd training job detail info tab
SS优化*推荐混排*收益统计.md|L51-L62|portal ps ego-portal ss prank dd ph training job detail
SS优化*收益统计 Ads.md|L5-L29|ps 训练 converter 任务 ego-train ss custom cpp*data_converter harbor shopeemobile
SS优化*收益统计 Ads.md|L32-L58|ps 训练 converter 任务 ego-train ss custom cpp*data_converter harbor shopeemobile
SS优化*收益统计 Ads.md|L61-L76|ps 训练 任务 ego-train worker ss search q2q v1 note
SS优化*收益统计 Ads.md|L77-L92|portal ps 训练 任务 ego-train ego-portal ss discovery ltr v1
SS优化*收益统计 Ads.md|L95-L110|ps 训练 任务 ego-train worker ss pctr*fusion_update v1 note ss_read_sample
SS优化*收益统计 Ads.md|L111-L125|portal ps 训练 任务 ego-train ego-portal ss esmm v1 harbor
SS优化*收益统计 Recommendation Recall* Rank.md|L3-L15|portal ps 训练 任务 ego-portal ss dd v1 training job
SS优化*收益统计 Recommendation Recall* Rank.md|L16-L29|portal ps 训练 任务 资源 ego-portal ss pdp v1 training
SS优化*收益统计 Recommendation Recall* Rank.md|L32-L45|portal ps 训练 任务 资源 ego-portal ss dd v1 training
SS优化*收益统计 Recommendation Recall* Rank.md|L46-L61|portal ps 训练 任务 ego-portal ss pdp v1 training job
SS优化*收益统计 Recommendation Recall* Rank.md|L62-L66|monitoring portal ps grafana 任务 ego-train ego-portal auc training job
SS优化*收益统计 Search粗排.md|L1-L8|portal ps ego-portal ss model model_management two_tower_listwise version tt_listwise_resflow_v46_regional_listwise_new job
SS优化*收益统计 Search粗排.md|L9-L16|portal ps ego-portal ss model model*management train_v1_prerank version prerank_v5_5_12_2_all_regions job
SS优化*收益统计 Search粗排.md|L17-L24|portal ps ego-portal ss model model*management train_v1_prerank version prerank_v6_1_dcn_v2_unified_full job
Sample Server Metrics.md|L5-L22|worker ss 耗时 processing time ms mainly describes communication process
Sample Server Metrics.md|L23-L30|worker ss dailyio wait time pod ms metric shows waiting
Sample Server Metrics.md|L33-L42|sampleserver coordinator ss hdfs file shows amount data files sent
Sample Server Metrics.md|L43-L46|ss pod shows amount data files processed each total 处理
Sample Server Metrics.md|L47-L52|worker ss speed per second provides fast pods process data
Sample Server Metrics.md|L53-L58|ss hdfs 耗时 ms shows time taken read write files
SampleServer中*数据文件解析报错*如何定位具体文件 \_Check failed* file*reader-\_num_row_groups\_\_ * 0*.md|L1-L4|ps parquet row_groups 问题 报错 解析 文件 发现 数量 相当于
SampleServer中*数据文件解析报错*如何定位具体文件 \_Check failed* file*reader-\_num_row_groups\_\_ * 0*.md|L9-L15|sampleserver 日志 ss cat log_file grep sampleprocessor start one file
SampleServer内存波动追查.md|L1-L5|portal ps ego-portal sample_server ss training job detail info tab
SampleServer内存波动追查.md|L6-L10|portal ps ego-portal sample_server ss training job detail info tab
SampleServer内存波动追查.md|L11-L15|portal ps ego-portal sample_server ss training job detail info tab
SampleServer内存波动追查.md|L16-L18|内存 ss batchfea 总结 波动 就是 由于 数据 缓存 导致
Scheduler[deprecated].md|L60-L68|cpu gpu model subset ram gb usage log 防护 措施
Score Discrepancy Debugging Guide.md|L1-L18|ps onnx ss debugging onnx-onnx optimizing graph optimization passes may
Score Discrepancy Debugging Guide.md|L19-L40|trt onnx debugging onnx-trt times inference score inconsistencies occur level
Scripts for using EgoPortal API.md|L1-L4|show help any script questions seek using command example
Scripts for using EgoPortal API.md|L7-L22|portal ps create_model sh tenant_name project_name model_name model_desc test cluster_region
Scripts for using EgoPortal API.md|L23-L42|portal ps create_model_version sh model_id model_path entry_file model_version_name model_version_desc test
Scripts for using EgoPortal API.md|L43-L99|portal mig ps ego_learner half_precision slot cpu kafka worker gpu
Scripts for using EgoPortal API.md|L102-L112|get_batch_platform_info sh cluster_region sg get available tenants projects info users
Scripts for using EgoPortal API.md|L113-L123|get_tag_enums sh cluster_region sg get list tags defined ego param
Scripts for using EgoPortal API.md|L124-L134|get_job_status_enums sh cluster_region sg get list job status param currently
Scripts for using EgoPortal API.md|L135-L149|portal ps get_job_status sh job_id verbose cluster_region sg get status
Scripts for using EgoPortal API.md|L150-L164|get_model_list sh project_name model_name page_id verbose account cluster_region sg get
Scripts for using EgoPortal API.md|L165-L179|portal ps get_model_version_list sh model_id model_version_name page_id verbose cluster_region sg
Scripts for using EgoPortal API.md|L180-L195|portal ps online_learning get_job_list sh model_version_id job_status tags page_id online_learning_job_list
Scripts for using EgoPortal API.md|L196-L211|checkpoint get_checkpoint_list sh model_id model_version_id page_id cluster_region sg get list
Scripts for using EgoPortal API.md|L212-L220|portal ps get_job_metrics sh job_id metric_duration hour round_name target_name cluster_region
Scripts for using EgoPortal API.md|L223-L234|portal ps delete_model sh model_id cluster_region sg delete model should
Scripts for using EgoPortal API.md|L235-L247|portal ps delete_model_version sh model_id model_version_id cluster_region sg delete model
Scripts for using EgoPortal API.md|L248-L259|portal ps ego_learner stop_job sh job_id cluster_region sg stop running
Scripts for using EgoPortal API.md|L260-L271|portal ps delete_job sh job_id cluster_region sg delete job record
Scripts for using EgoPortal API.md|L272-L283|portal ps checkpoint delete_checkpoint sh checkpoint_id cluster_region sg delete egocontroller
Scripts for using EgoPortal API.md|L286-L304|publish get_online_model_list sh online_model_name tenant_name project_name page_id verbose account offline_model_version_id
Scripts for using EgoPortal API.md|L305-L318|get_online_job_list sh online_model_id job_status page_id cluster_region sg get job list
Scripts for using EgoPortal API.md|L319-L351|portal predictor ps online_learning half_precision onlineps converter grey_release compile publish
Scripts for using EgoPortal API.md|L354-L367|portal ps pull_log sh tenant_name project_name job_id cluster_region sg get
Scripts for using EgoPortal API.md|L368-L380|move_model sh model_name target_project_name cluster_region sg move model designated project
Scripts for using EgoPortal API.md|L381-L394|portal ps ego_learner compile local_compile sh model_path entry_file image cluster_region
Scripts for using EgoPortal API.md|L395-L408|checkpoint sync_checkpoint sh target_model_id target_model_version_id checkpoint_id source_cluster target_cluster copy under
Search GPU图优化一期.md|L11-L18|ps trt gpu ab peak qps model name version type
Search GPU图优化一期.md|L19-L24|gpu ctr 线上 缩容 验证 卡月 流量 平稳 缩容后 利用率
Search GPU图优化一期.md|L25-L31|模型 上线 gpu cvr gpu_search_cvr_id_552_mpi_add_video_bf16 subset latency ms 线上 验证
Seastar vs brpc.md|L5-L12|cpu ss experiment settings use client process send request repeatedly
Seastar vs brpc.md|L13-L20|cpu big packet performance each request contains kb user data
Seastar vs brpc.md|L21-L27|cpu small packet performance each request response contains only rpc
Sparse Feature Memory Optimization.md|L7-L16|sparse feature optimization effect general these optimizations reduce memory consumption
Sparse Feature Memory Optimization.md|L17-L20|apply memory optimization turn configuring online-export yaml file specifically add
Sparse input module.md|L1-L8|slot sparse feature feature_type param currently there three kinds input
Sparse input module.md|L9-L12|serving sparse feature ss feature_type common input denotes values samples
Sparse input module.md|L13-L16|sparse feature feature_type item usually used list-wise model input set
Sparse input module.md|L17-L20|sparse feature feature_type undefined input neither used folding user side
Sparse input module.md|L25-L30|sparse dense feature use_nsc param like ego0 ego1 supports nsc
Sparse input module.md|L31-L40|ps slot feature seq slots divide sequence multiple groups transformed
Sparse input module.md|L41-L43|ps ss seq sample format please refer design docs google
Speed BenchMarks.md|L4-L5|portal ps cpu 任务 worker 资源 ego-portal ss search_ranking_deep_cvr device
Speed BenchMarks.md|L6-L7|portal ps cpu 任务 worker 资源 ego-portal ss dd_din_lt_esmm_mpi_softsim_2k_cl_adf_mgdcn_v2_br device
Speed BenchMarks.md|L8-L9|portal ps cpu 任务 worker release 资源 ego-portal ss dsrm_v5_release
Speed BenchMarks.md|L10-L11|portal ps cpu 任务 worker 资源 ego-portal ss pdp_dinv6_lt_simnet_ego1_l3_vnt2_vn device
Speed BenchMarks.md|L12-L13|portal ps cpu 任务 a30 worker gpu 资源 ego-portal ss
Speed BenchMarks.md|L14-L15|portal ps cpu 任务 a30 worker gpu 资源 ego-portal ss
Speed BenchMarks* 1*8_3.md|L4-L5|portal ps cpu 任务 worker 资源 ego-portal ss search_ranking_deep_cvr device
Speed BenchMarks* 1*8_3.md|L6-L7|portal ps cpu 任务 worker 资源 ego-portal ss dd_din_lt_esmm_mpi_softsim_2k_cl_adf_mgdcn_v2_br device
Speed BenchMarks* 1*8_3.md|L8-L9|portal ps cpu 任务 worker release 资源 ego-portal ss dsrm_v5_release
Speed BenchMarks* 1*8_3.md|L10-L11|portal ps cpu 任务 worker 资源 ego-portal ss pdp_dinv6_lt_simnet_ego1_l3_vnt2_vn device
Speed BenchMarks* 1*8_3.md|L12-L13|portal ps cpu 任务 a30 worker gpu 资源 ego-portal ss
Speed BenchMarks* 1*8_3.md|L14-L15|portal ps cpu 任务 a30 worker gpu 资源 ego-portal ss
Speed BenchMarks* 1*8_4.md|L4-L5|portal ps cpu 任务 worker 资源 ego-portal ss search_ranking_deep_cvr device
Speed BenchMarks* 1*8_4.md|L6-L7|portal ps cpu 任务 worker 资源 ego-portal ss dd_din_lt_esmm_mpi_softsim_2k_cl_adf_mgdcn_v2_br device
Speed BenchMarks* 1*8_4.md|L8-L9|portal ps cpu 任务 worker release 资源 ego-portal ss dsrm_v5_release
Speed BenchMarks* 1*8_4.md|L10-L11|portal ps cpu 任务 worker 资源 ego-portal ss pdp_dinv6_lt_simnet_ego1_l3_vnt2_vn device
Speed BenchMarks* 1*8_4.md|L12-L13|portal ps cpu 任务 a30 worker gpu 资源 ego-portal ss
Speed BenchMarks* 1*8_4.md|L14-L15|portal ps cpu 任务 a30 worker gpu 资源 ego-portal ss
Speed BenchMarks.md|L4-L5|portal ps cpu 任务 worker 资源 ego-portal ss search_ranking_deep_cvr device
Speed BenchMarks.md|L6-L7|portal ps cpu 任务 worker 资源 ego-portal ss dd_din_lt_esmm_mpi_softsim_2k_cl_adf_mgdcn_v2_br device
Speed BenchMarks.md|L8-L9|portal ps cpu 任务 worker release 资源 ego-portal ss dsrm_v5_release
Speed BenchMarks.md|L10-L11|portal ps cpu 任务 worker 资源 ego-portal ss pdp_dinv6_lt_simnet_ego1_l3_vnt2_vn device
Speed BenchMarks.md|L12-L13|portal ps cpu 任务 a30 worker gpu 资源 ego-portal ss
Speed BenchMarks.md|L14-L15|portal ps cpu 任务 a30 worker gpu 资源 ego-portal ss
Speed up Online Inference.md|L1-L6|serving emb cache tensor offline training using online example there
Speed up Online Inference.md|L7-L11|folded user side inputs online service received usually lot item
TF fp16离线测试结果.md|L1-L7|模型 trt tensorrt gpu ss t4 耗时 pdp stream count
TF fp16离线测试结果.md|L8-L11|模型 trt tensorrt gpu ss 耗时 cart stream count model
TF fp16离线测试结果.md|L12-L19|模型 trt tensorrt gpu ss 耗时 dd stream count model
TF fp16离线测试结果.md|L20-L41|编译 模型 trt 样本 gpu 耗时 xla tf fp16 pdp
TF fp16离线测试结果.md|L42-L48|monitoring predictor 模型 ps 监控 发布 grafana gpu egopredictor tf
TF fp16跑图.md|L3-L10|编译 模型 tensorrt 推理 半精度 onnx 耗时 xla fp16 fp32
TF fp16跑图.md|L11-L14|推理 半精度 onnx fp32 cast fp16 实现 方式 参考 做法
TF fp16跑图.md|L15-L18|gpu tf fp16 pdp cart ab 效果 测试 服务 离线
TF fp16跑图.md|L19-L34|模型 tensorrt gpu 吞吐 耗时 cart pdp cuda stream batch
TF fp16跑图.md|L35-L46|模型 tensorrt 推理 gpu checkpoint 耗时 gpu_pdpv5_ego1_multilabel_vc_sr_lite pdp fp16 ab
TF fp16跑图.md|L47-L56|模型 tensorrt 半精度 gpu 耗时 ab tf fp16 te 总结
TF fp16跑图.md|L61-L67|monitoring predictor 模型 ps 监控 发布 grafana egopredictor tf fp16
Teacher-Student模型联合训练方案初版.md|L1-L7|模型 训练 teacher-student teacher student 联合 会去 校准 结果 单独
Teacher-Student模型联合训练方案初版.md|L14-L19|模型 训练 ss ego teacher-graph pb teacher-student-graph teacher session run
Teacher-Student模型联合训练方案初版.md|L20-L25|ckpt 模型 参数 sparse dense teacher-student tf import_graph_def teacher-graph pb
Teacher-Student模型联合训练方案初版.md|L26-L47|编译 模型 配置 serving 训练 任务 compile teacher student model_version
Teacher-Student模型联合训练方案初版.md|L48-L52|模型 训练 teacher hdf5 tf keras models load_model save_model sequential
Teacher-Student模型联合训练方案最终版.md|L1-L7|模型 训练 teacher-student teacher student 联合 会去 校准 结果 单独
Teacher-Student模型联合训练方案最终版.md|L14-L40|ckpt 模型 配置 训练 参数 checkpoint teacher tf stop_gradient freeze_model_param
Teacher-Student模型联合训练方案最终版.md|L41-L49|模型 ps 参数 sparse 任务 特征 checkpoint controller student teacher
Teacher-Student模型联合训练方案最终版.md|L50-L56|编译 ckpt 模型 任务 compile checkpoint controller checkpointid model_version_name checkpoint_path
Teacher-Student模型联合训练方案最终版.md|L57-L59|训练 slot sparse 任务 checkpoint save_checkpoint slots nn 完成 之后
Test model locally.md|L19-L50|feature ss debug validation fail keep only one sample mv
Test model locally.md|L51-L78|ps feature ss trace proto git garena recommend srec_protos generate
Test model locally.md|L79-L93|ps itemid int requests post host port upservice trace data
The file structure of model materials.md|L4-L7|compile model_files folder there model-design files compiled ego-api-v1 should keep
The file structure of model materials.md|L8-L11|converter run_files folder there files used job running such converter_stable
The file structure of model materials.md|L12-L14|ego-learner config_files folder there config files ego job such yaml
The model pipeline in egotf 0_4_3.md|L5-L15|serving compile ego-learner model compiling design use ego is_training_mode distinguish
The model pipeline in egotf 0_4_3.md|L16-L19|slot checkpoint ss hdfs training launch cmd bash ego-api train_k8s_openapi
The model pipeline in egotf 0_4_3.md|L20-L26|serving emb embedding checkpoint online export task responsible generate validate
The model pipeline in egotf 0_4_3.md|L27-L33|serving slot publish ss hdfs packing publishing serving_path python ego-api
The usage of resources when GPU pooling and Dense allreduce.md|L3-L23|ps sparse 带宽 ss v100 mock round pull batch bytes
The usage of resources when GPU pooling and Dense allreduce.md|L24-L49|portal mig ps a30 ego-portal 带宽 ss iftop live-test training
Three different modes for reading data in a logic day from multiple data folders.md|L9-L18|feature reading data logic day multiple paths new demo according
Three different modes for reading data in a logic day from multiple data folders.md|L19-L29|feature reading data logic day multiple paths batch composed samples
Three different ways to cache data in Worker.md|L3-L17|portal ps ego_learner sampleserver worker ego-learner ss use_new_io launch_job sh
Three different ways to cache data in Worker.md|L18-L26|portal ps ego_learner sampleserver worker ego-learner ss use_new_io launch_job sh
Time and resource consumption analysis between parquet and plain text.md|L3-L12|feature ss hdfs env spark75 threads data r2 projects rcmd_feature
Time and resource consumption analysis between parquet and plain text.md|L13-L20|ps feature hdfs env spark75 threads data r2 projects rcmd_feature
Time and resource consumption analysis between parquet and plain text.md|L23-L30|worker feature hdfs env cluster sg-10 data r2 projects rcmd_feature
Time and resource consumption analysis between parquet and plain text.md|L31-L35|time consumptions result1 seconds result2
Time and resource consumption analysis between parquet and plain text.md|L36-L40|monitoring ps grafana ego-train memory consumptions result1 infra sz muvhwlwnz
Time and resource consumption analysis between parquet and plain text.md|L41-L48|worker feature hdfs env cluster sg-10 data r2 projects rcmd_feature
Time and resource consumption analysis between parquet and plain text.md|L49-L53|time consumptions result1 seconds result2
Time and resource consumption analysis between parquet and plain text.md|L54-L58|monitoring ps grafana ego-train memory consumptions result1 infra sz muvhwlwnz
Torch deepctr_ddp打平记录.md|L1-L2|portal deepctr ps benchmark ego-portal benchmark_deepctr model_version auc last day
Train job卡点追踪技术方案.md|L5-L21|portal 训练 磁盘 告警 supervisor job jobkiller dod 整体 流程
Train job卡点追踪技术方案.md|L22-L58|配置 训练 任务 告警 gpu rules rule_id diskfilecreatefailed severity p0
Train job卡点追踪技术方案.md|L59-L63|训练 任务 告警 快照 bigint unsigned primary key rule_id varchar
Train job卡点追踪技术方案.md|L64-L107|训练 任务 告警 快照 rule ruleinstance job eventsource executor jobkiller
Train job卡点追踪技术方案.md|L108-L110|ps ego train job docs google document pi-3cvf6vb093rv-t_w9djzkaspnbctnlh6nmww76-a edit tab
Training Models.md|L1-L6|ps ss logic day mentioned data organization tutorial ego v1
Training Models.md|L7-L18|ss training process logic day samples figure above reveals overall
Tutorial of EGO V1_0.md|L89-L114|worker coordinator ss model-run ego there three roles distributed training
Tutorial of EGO V1_0.md|L115-L146|ps notebook ego-train ss running custom ego-train-v1 build here steps
Tutorial of EGO V1_0.md|L147-L153|ego-predictor predictor ps onlineps ego-train ego-ps used storing updating training
Tutorial of EGO V1_0.md|L154-L158|ps optimizers ego-ps mentioned updating training params duty list implemented
Tutorial of EGO V1_0.md|L159-L164|ego-predictor predictor ps publish egopredictor online inference platform finishing offline
Tutorial of EGO V1_0.md|L165-L168|ego-controller brain ego responsible interacting users scheduling jobs supervising
Tutorial of EGO V1_0.md|L169-L186|portal ps ego-portal egoportal there two methods submit job one
Tutorial of EGO V1_0.md|L187-L190|egoscheduler acts commander ego-controller managing resources traffic
Tutorial of EGO V1_0.md|L191-L194|egosupervisor acts teacher cares status other measures each job
Tutorial.md|L3-L8|data organization training should divided datasets according sample timestamp format
Tutorial.md|L9-L14|ps model design build up deep allowed apply most tensorflow
Tutorial.md|L15-L20|sparse dense feature declare inputs acoording type there input obtain
Tutorial.md|L21-L26|mig ss design model structure processing inputs good enhance ability
Tutorial.md|L27-L43|ss declare targets rounds target ego want print out various
Tutorial.md|L44-L54|evict ego-train compile feature ss admission generate compiled files mentioned
Tutorial.md|L55-L66|feature advanced features illustration above only demonstrates basic pipeline building
Tutorial.md|L67-L70|model train organizing data defining
Tutorial.md|L71-L94|egotrain worker coordinator ss declare framework ego there three roles
Tutorial.md|L95-L103|egotrain predictor ps onlineps egopredictor optimizers egops used storing updating
Tutorial.md|L104-L107|ps organize files right way please follow demo organise file
Tutorial.md|L108-L111|ps submit training job there several steps see
Tutorial.md|L114-L117|ps publish well-trained model there several steps see
Tutorial.md|L118-L122|release ss self debug find problems during training process self-debug
US A100机器性能测试.md|L1-L16|ps 训练 emb cpu 显存 样本 embedding worker a100 gpu
US A100机器性能测试.md|L17-L27|portal 模型 ps cpu a30 gpu ego-portal din live-test training
US A100机器性能测试.md|L28-L32|round0 模型 round1 训练 a100 round round2 din c3v3 ins
US A100机器性能测试.md|L33-L34|round0 模型 round1 训练 a30 a100 din ins round2 对比
US A100机器性能测试.md|L35-L41|round0 模型 round1 训练 样本 a30 a100 din unit ins
US A100机器性能测试.md|L42-L57|ps 训练 cpu 显存 样本 a100 gpu dense 内存 ss
US A100机器性能测试.md|L58-L59|模型 ps 训练 cpu sparse gpu din util mem cores
Update* Time and resource consumption analysis between parquet and plain text _using C\_\_ parquet-parser tool_.md|L3-L10|worker feature hdfs env cluster sg-10 data r2 projects rcmd*feature
Update* Time and resource consumption analysis between parquet and plain text _using C\_\_ parquet-parser tool_.md|L15-L18|monitoring ps grafana ego-train memory consumptions result1 infra sz muvhwlwnz
Update* Time and resource consumption analysis between parquet and plain text \_using C\_\_ parquet-parser tool*.md|L19-L26|worker feature hdfs env cluster sg-10 data r2 projects rcmd*feature
Update* Time and resource consumption analysis between parquet and plain text _using C\_\_ parquet-parser tool_.md|L31-L34|monitoring ps grafana ego-train memory consumptions result1 infra sz muvhwlwnz
Update* Time and resource consumption analysis between parquet and plain text \_using C\_\_ parquet-parser tool*.md|L35-L37|conclusion time memory consumptions indifferent between parsing data plain text
Upgrade TF-1 to TF-2.md|L3-L6|ss direct replacement observation without code changes resulted suboptimal performance
Upgrade TF-1 to TF-2.md|L7-L12|xla ii autoconfig observation initial experiments optimization showed mixed results
Upgrade TF-1 to TF-2.md|L13-L18|mig cpu iii version-specific optimizations observation despite migration tf2 some
Upgrade TF-1 to TF-2.md|L19-L27|ss iv fine-tuning run options batch sizes observation certain scenarios
User Debug Manual.md|L1-L6|compile view logs provide methods method3 method4 used real time
User Debug Manual.md|L7-L17|portal ps ego-portal method1 egoportal web ui view log file
User Debug Manual.md|L18-L27|ss method2 s3cmd use way download all log files related
User Debug Manual.md|L28-L31|method3 company log platform search some keywords within directly
User Debug Manual.md|L38-L65|portal ps ego-portal find cause through job log get list
User Debug Manual.md|L66-L71|ps some useful keywords locate root cause best practise follow
User Debug Manual.md|L88-L90|other key words error fail errno received signal
User Self-Definition LR Scheduler.md|L3-L6|ps l4 design docs google document jklyxse8xzl4ahmibpiaeebip8x3ioiywyrr9blmaze edit usp sharing
User Self-Definition LR Scheduler.md|L7-L10|ps demo git garena ego-public ego-api-v1 tree master tensorflow lrate*strategy
User Self-Definition LR Scheduler.md|L11-L18|emb ss function description support user self-definition lr scheduler strategy
User Self-Definition LR Scheduler.md|L19-L26|worker ss introductions use users call ego-api interface model definition
User Self-Definition LR Scheduler.md|L27-L40|ss python api define lr scheduler strategy half_strategy_id ego new_lrate_strategy
User Self-Definition LR Scheduler.md|L41-L57|ps converter train_config ego-learner lr scheduler calculation file user needs
Using multiple sparse inputs and folded-mode \_egotf 0_4_3 and above*.md|L5-L19|slot sparse ss multiple inputs folded-mode ego get*slots slot_ids slot_dims
Using multiple sparse inputs and folded-mode \_egotf 0_4_3 and above*.md|L20-L26|converter dense feature ss input folded-mode ego get*dense_feature name dim
V1_3_2 benchmark model performance.md|L5-L37|deepctr 模型 ps 训练 样本 sparse 任务 benchmark 资源 checkpoint
V1_3_3_rc1 benchmark model performance.md|L3-L5|portal 模型 ps cpu 任务 worker ego-portal ss core metrics
V1_3_3_rc1 benchmark model performance.md|L6-L7|portal deepctr 模型 ps cpu 任务 worker benchmark ego-portal ss
V1_3_3_rc2 benchmark model performance.md|L3-L4|online-learning 模型 ps cpu 任务 ego-train worker ss core metrics
V1_3_3_rc2 benchmark model performance.md|L5-L6|portal deepctr 模型 ps cpu sparse 任务 worker benchmark ego-portal
V1_3_3_rc3 benchmark model performance.md|L3-L4|模型 ps cpu 任务 core metrics configures refer ego avg
V1_3_3_rc3 benchmark model performance.md|L5-L6|portal deepctr 模型 ps cpu sparse 任务 worker benchmark ego-portal
V1_4_0 benchmark model performance.md|L3-L5|portal 模型 ps cpu 任务 worker ego-portal ss core metrics
V1_4_0 benchmark model performance.md|L6-L7|portal deepctr 模型 ps cpu 任务 worker benchmark ego-portal ss
V1_4_0_1 benchmark model performance.md|L3-L5|模型 cpu 任务 core metrics configures refer avg samples usage
V1_4_0_1 benchmark model performance.md|L6-L7|portal deepctr 模型 ps cpu 任务 worker benchmark ego-portal ss
V1_4_0_2-zjz benchmark model performance \_Merge feature_ego-plugin-dev-bak*.md|L3-L5|模型 cpu 任务 core metrics configures refer avg samples usage
V1*4_0_2-zjz benchmark model performance \_Merge feature_ego-plugin-dev-bak*.md|L6-L7|portal deepctr 模型 ps cpu 任务 benchmark ego-portal metrics configuration
V1*5_0 benchmark model performance.md|L3-L4|portal 模型 ps cpu 任务 worker ego-portal ss core metrics
V1_5_0 benchmark model performance.md|L5-L6|portal deepctr 模型 ps cpu 任务 worker benchmark ego-portal ss
V1_5_1 benchmark model performance.md|L1-L4|portal deepctr ps ego-portal live-test training job detail nobreadcrumb tab
V1_5_1 benchmark model performance.md|L5-L8|portal ps ego-portal din live-test training job detail nobreadcrumb tab
V1_5_1 benchmark model performance.md|L9-L11|portal ps sparse ego-portal sparse_dnn_adf live-test training job detail nobreadcrumb
V1_6_0 benchmark model performance.md|L1-L2|模型 ps cpu 任务 worker 资源 ss core metrics new
V1_6_0 benchmark model performance.md|L3-L4|portal deepctr 模型 ps cpu 任务 worker benchmark 资源 ego-portal
V1_7_0 benchmark model performance.md|L1-L3|portal 模型 ps cpu 任务 worker 资源 ego-portal ss core
V1_7_0 benchmark model performance.md|L6-L9|portal deepctr ps ego-portal live-test training job detail nobreadcrumb tab
V1_7_0 benchmark model performance.md|L10-L13|portal ps ego-portal din live-test training job detail nobreadcrumb tab
V1_7_0 benchmark model performance.md|L14-L16|portal ps sparse ego-portal sparse_dnn_adf live-test training job detail nobreadcrumb
V1_8_0 benchmark model performance.md|L1-L14|deepctr cpu sparse benchmark gpu ss correctness benchmarks model name
V1_8_0 benchmark model performance.md|L15-L34|cpu benchmark release gpu speed benchmarks model name search_ranking_deep_cvr complete
V1_8_2 benchmark model performance.md|L1-L14|deepctr cpu sparse benchmark gpu ss correctness benchmarks model name
V1_8_2 benchmark model performance.md|L15-L34|cpu benchmark release gpu speed benchmarks model name search_ranking_deep_cvr complete
V1_8_3 benchmark model performance.md|L1-L14|deepctr cpu sparse benchmark gpu ss correctness benchmarks model name
V1_8_3 benchmark model performance.md|L15-L34|cpu benchmark release gpu speed benchmarks model name search_ranking_deep_cvr complete
V1_8_4 benchmark model performance.md|L1-L14|deepctr cpu sparse benchmark gpu ss correctness benchmarks model name
V1_8_4 benchmark model performance.md|L15-L34|cpu benchmark release gpu speed benchmarks model name search_ranking_deep_cvr complete
Variable embedding length survey.md|L1-L6|ps emb embedding feature basic idea paper link arxiv pdf
Variable embedding length survey.md|L7-L12|emb embedding feature paper experiment result variable applied fields related
Variable embedding length survey.md|L13-L23|ps emb embedding ego-train work implement ego ego-ps decide exact
Variable embedding length survey.md|L24-L27|slot emb embedding coarse simulation testify idea ego count frequency
Video Ads Models Inference Optimization.md|L1-L6|optimizations fuse_splits_into_slice merge consecutive concat inputs come split nodes turn
View and operate model & version.md|L1-L5|ss delete model operation permission only creator admin there no
View and operate model & version.md|L6-L18|ps shell delete_model sh delete_mode model_id delete model should firstly
View and operate model & version.md|L21-L29|checkpoint ss view model version list versions under inherit tenant
View and operate model & version.md|L30-L44|ps shell get_model_version_list sh model_id model_version_name page_id get model version
View and operate model & version.md|L45-L49|ss delete model version operation permission only creator admin there
View and operate model & version.md|L50-L63|ps shell delete_model_version sh model_id model_version_id delete model version param
View and operate model & version.md|L64-L70|ckpt publish release checkpoint ss view list click go operation
View and operate model & version.md|L71-L86|checkpoint shell get_checkpoint_list sh model_id model_version_id page_id get list under
View and operate online model.md|L1-L6|view online model detail once go details page users job
View and operate online model.md|L7-L20|shell get_online_job_list sh online_model_id job_status page_id get job list online
View and operate training job.md|L1-L6|grafana checkpoint view training job detail once go details page
View and operate training job.md|L7-L22|ps shell get_job_status sh job_id verbose get status info job
View and operate training job.md|L29-L41|ps ego_learner shell stop_job sh job_id stop running job param
View and operate training job.md|L46-L57|ps shell delete_job sh job_id delete job record database param
What is \_round* and _target**.md|L1-L17|ss concept definition target ego want print various metrics like
Worker Eval One Pass 方案.md|L13-L28|ckpt eval 训练 ss use last day last_day_eval_ratio flags txt
Worker Eval One Pass 方案.md|L29-L43|portal eval ps 任务 ego-portal gflag training job detail info
Worker Metrics.md|L5-L18|训练 样本 ss training speed performance metric indicates quickly machine
Worker Metrics.md|L19-L50|训练 耗时 batch training speed ms performance metric indicates quickly
Worker Metrics.md|L51-L72|worker minibatch ss 耗时 preload batch ms performance metric measures
Worker Metrics.md|L73-L91|样本 day batch count performance metric shows number batches current
ZK ** Redis Migration Guidance.md|L3-L4|ss singapore sg service zookeeper address ads zk-ai-platform-ego-ads-sg-live-8petn79c global live
ZK ** Redis Migration Guidance.md|L5-L6|ss united states us service zookeeper address ads zk-ai-platform-ego-ads-us-live-w4aq4etm global
ZK ** Redis Migration Guidance.md|L9-L57|ego-predictor predictor dependency upgrade direct ego-predictor-client version note predictv4 protocol
ZK \_\_ Redis Migration Guidance.md|L58-L67|ego-predictor predictor ps go dependency upgrade merge request ego ego-predictor-client-go
[A]Ego New Member Guide(used by EGO members internally).md|L1-L18|wc note document mainly contains some information permit application introduction
[A]Ego New Member Guide(used by EGO members internally).md|L19-L20|ps ss ii main platforms systems platform user link description
[A]Ego New Member Guide(used by EGO members internally).md|L21-L28|配置 bj ip arthur hu 开发 创建 一下 账号 首次
[A]Ego New Member Guide(used by EGO members internally).md|L29-L36|ss sg ip smc ssh space cmdb data 开发 现在
[A]Ego New Member Guide(used by EGO members internally).md|L39-L57|serving ss cmdb permissions privileges query machine corresponding services toc
[A]Ego New Member Guide(used by EGO members internally).md|L58-L67|ss toc permissions apply space shown following figure seek authorization
[A]Ego New Member Guide(used by EGO members internally).md|L68-L71|ss sam permissions apply backup approver permission able approve others
[A]Ego New Member Guide(used by EGO members internally).md|L72-L77|kafka ss dmp permissions using di team specify project corresponding
[A]Ego New Member Guide(used by EGO members internally).md|L78-L83|ps ss group permission space utility swp ticket_creation template apply_shopee_jira_
[A]Ego New Member Guide(used by EGO members internally).md|L84-L103|ps iv ego platform basic information currently includes several directions
[A]Ego New Member Guide(used by EGO members internally).md|L106-L112|feature various abbreviations mean refer machine learning platform ego no
[A]Ego New Member Guide(used by EGO members internally).md|L113-L118|ss t4 development machines access git garena default only personal
[A]Ego New Member Guide(used by EGO members internally).md|L119-L132|ps ss development machine cannot use vs code remote ssh
[A]Ego New Member Guide(used by EGO members internally).md|L133-L136|ps ss there timeout logging develop machine error*server_connection_timeout please try
[A]Ego New Member Guide(used by EGO members internally).md|L137-L140|hdfs install spark hadoop toc machines path ego r2 projects
[A]Ego New Member Guide(used by EGO members internally).md|L141-L148|ps release ss break down limitation network transferring between development
[A]Ego New Member Guide(used by EGO members internally).md|L149-L160|ps ss apply hadoop permission click datasuite ram my projects
[A]Ego New Member Guide(used by EGO members internally).md|L161-L174|run spark job vim bashrc source sdi credentials entrypoint sh
[Dev]How_to_compose_update_the_worker's_docker_image.md|L3-L10|ps prepare image enter container docker pull harbor shopeemobile di-driver
[Dev]How_to_compose_update_the_worker's_docker_image.md|L11-L18|ss operations container apt install liblzo2-2 openssh-server mkdir run sshd
[Dev]How_to_compose_update_the_worker's_docker_image.md|L19-L26|worker operations out container docker cp openmpi-4 xxx should copied
[Dev]How_to_compose_update_the_worker's_docker_image.md|L27-L36|ps compile worker ego-learner update image latest please refer use
[EGO] Portal User Manual.md|L1-L8|sparse feature ego product basic information position ndustrial deep learning
[EGO] Portal User Manual.md|L11-L25|portal ego links offers three different environments various usage scenarios
[EGO] Portal User Manual.md|L26-L29|portal ps feature ego core features support end-to-end solution provides
[EGO] Portal User Manual.md|L30-L45|portal ps notebook user manual model version src contextnavpagetreemode training
[EGO]Supervisor Competitors.md|L15-L18|监控 训练 任务 日志 bytedance webshell 机器 学习 平台 支持
[EGO]Supervisor Competitors.md|L19-L25|训练 参数 任务 部署 资源 task list timeline 列表 状态
[EGO]Supervisor Competitors.md|L26-L32|monitoring cpu 显存 gpu 内存 利用率 使用量 网络 流入 速率
[EGO]Supervisor Competitors.md|L33-L38|ps 训练 日志 log lucene error volc ml_task logs volcengine
[EGO]Supervisor Competitors.md|L39-L42|webshell 实例 状态 运行 进入 容器 内部 手动 执行命令 排查
[EGO]Supervisor Competitors.md|L51-L54|监控 日志 bytedance webshell 机器 学习 平台 支持 查看 服务
[EGO]Supervisor Competitors.md|L55-L61|参数 部署 instance list 列表 服务 状态 实例 数量 代表
[EGO]Supervisor Competitors.md|L62-L70|monitoring 监控 cpu 显存 gpu 内存 单击 某个 实例 操作
[EGO]Supervisor Competitors.md|L71-L76|训练 日志 log lucene error 支持 语法 全文检索 填写 检索
[EGO]Supervisor Competitors.md|L77-L88|回滚 模型 配置 参数 版本 changes service 扩缩容 当前 业务量
[EGO]Supervisor Competitors.md|L91-L99|monitoring ps 监控 cpu 资源 内存 ti-ems qps xx bps
[EGO]Supervisor Competitors.md|L100-L110|模型 监控 配置 告警 alarms ti-ems ti 服务 策略 从而
[EGO]Supervisor Competitors.md|L111-L114|模型 推理 日志 log 进入 在线 批处理 作业 页面 单击
[Tencent] The distributed machine learning platform -- Wuliang.md|L3-L11|introduction order solve training problem large samples deploying very models
[Tencent] The distributed machine learning platform -- Wuliang.md|L12-L15|system architecture wuliang shown below
[Tencent] The distributed machine learning platform -- Wuliang.md|L16-L25|ss computing framework there three key dimensions system design objectives
[Tencent] The distributed machine learning platform -- Wuliang.md|L26-L31|worker ss parameter acquisition practical training very large scale models
[Tencent] The distributed machine learning platform -- Wuliang.md|L32-L41|ss gradient update upload calculation large amount data transferred over
[Tencent] The distributed machine learning platform -- Wuliang.md|L42-L47|cpu ss gradient computation deep learning model involves large number
[Tencent] The distributed machine learning platform -- Wuliang.md|L48-L53|feature ss whole process model management recommendation business interests users
[Tencent] The distributed machine learning platform -- Wuliang.md|L54-L66|problem model on-line performance due very large models hundreds billions
[Tencent] The distributed machine learning platform -- Wuliang.md|L67-L70|model services use large models hundreds billions parameters online forecasting
[Tencent] The distributed machine learning platform -- Wuliang.md|L71-L75|ss memory problem model loading loaded associated data structures constructed
[Tencent] The distributed machine learning platform -- Wuliang.md|L76-L89|ss performance issues model service order achieve good user experience
[V1.2_L40S]2025-10-14.md|L11-L13|l40s ps l4 cpu gpu batching qps latency cores gputl
[V1.2_L40S]2025-10-14.md|L14-L15|l40s ps l4 cpu gpu batching qps latency cores gputl
[Volcengine] Machine Learning Platform.md|L1-L14|introduction ultra-large scale distributed training support running tasks including variety
\_2024-10-28_30**ads_upshop**core in psclient*.md|L1-L8|coredump predictor ps 监控 onlineps egopredictor search ads prerank upshop
_2024-10-28_30**ads_upshop**core in psclient_.md|L9-L48|predictor ps 监控 同步 onlineps 参数 egopredictor 内存 oom sre
_2024-10-28_30**ads_upshop**core in psclient_.md|L49-L105|predictor ps egopredictor 版本 todo incomplete psclient pb315 core conan
_20240627_oneDNN_disable JIT.md|L1-L10|调优 cpu 资源 内存 xla summary onednn intel allocator data
\_20240627_oneDNN_disable JIT.md|L11-L37|模型 ps cpu 延迟 performence video pod ms qps 最终
\_20240627_oneDNN_disable JIT.md|L38-L47|cpu 延迟 吞吐 pdp us d16v3 tfrun 结论 本次 推全后
\_20240627_oneDNN_disable JIT.md|L48-L53|ps cpu video2 qps latency avg ms us 集群 压测
\_A_Database dev**live.md|L1-L3|ss db cluster env username password database name dev test
\_A_Database dev**live.md|L4-L6|ps design guide please follow internal database guideline qy65
\_A_Dev _ Test environment.md|L1-L4|egotrain ss hdfs machine list hostname ip desc bj-train office
_A_Dev _ Test environment.md|L5-L14|ps compile ss ssh access create toc ticket space service
_A_Dev _ Test environment.md|L15-L18|ss git access sp already exposed socks5 port proxy connection
_A_Dev _ Test environment.md|L19-L26|ss method save below code home bin scmd add path
_A_Dev _ Test environment.md|L27-L30|ss ssh method add those lines remote home config file
_A_Dev _ Test environment.md|L31-L40|ps release ss vscode remote development add those lines home
_A_Dev _ Test environment.md|L41-L43|ss access target instance returns permission error like error*ssh_authentication visit
\_Case Study**2022-04-29**up2my-dd*.md|L1-L12|模型 发布 release 内存 版本 background bug item version some
_Case Study**2022-04-29**up2my-dd_.md|L13-L32|release 内存 ss 版本 issue analysis release-2022-04-28 tf*newtensor tensor version
\_Case Study**2022-04-29**up2my-dd*.md|L33-L65|内存 action complete abort memory align unique tensors actually usually
_Case Study**2022-11-01**up-mpi_.md|L1-L8|grafana background vince liwei mpi team told us they got
_Case Study**2022-11-01**up-mpi_.md|L9-L14|ps solution script sync ips zookeeper dns just run case
_Case Study**2022-11-01**up-mpi_.md|L15-L44|ps ss issue analysis error strange vince really got model
_Case Study**2022-11-01**up-mpi_.md|L45-L61|mig ps release ss action complete fix original alert rules
_Case Study**2023-04-21**egopredictor-map_.md|L17-L21|map ego grpc dns ip zk usage go 问题 分析
_Case Study**2023-08-18**egopredictor-map_.md|L1-L10|回滚 发布 版本 kube-ego-inference-sg-general-b-live map-map ram recommend service appid appmodelname
_Case Study**2023-08-18**egopredictor-map_.md|L11-L20|回滚 部署 liveish live pod 问题 背景 测试 镜像 没有
_Case Study**2023-08-18**egopredictor-map_.md|L21-L30|模型 sparse dense 内存 validate value model*conf json tensor memcpy
\_Case Study**2023-08-18**egopredictor-map*.md|L31-L48|模型 ps 日志 dense q1 q2 qps q3 memcpy q4
_Case Study**2023-08-18**egopredictor-map_.md|L49-L50|predictor ps 监控 配置 告警 eta bug wyatt guo git
_Case Study**2023-08-18**gpuupdd_.md|L1-L12|coredump 模型 发布 配置 guangya wu mailto ranker submodel plugin
_Case Study**2023-08-18**gpuupdd_.md|L13-L18|coredump 模型 发布 gpu gpuupdd dynamic 影响 期间 大约 打向
_Case Study**2023-08-18**gpuupdd_.md|L19-L26|编译 coredump 模型 trt 配置 onnx xla 版本 guangya plugin
_Case Study**2023-08-18**gpuupdd_.md|L27-L28|predictor 模型 ps eta bug shuquan huang git garena recommend
_Case Study**2023-11-02**guardian_.md|L19-L35|回滚 predictor ps 配置 guardian 上线 部署 版本 action complete
_Case Study**2024-7-20**gpudd-dynamic_.md|L1-L8|coredump 模型 gpu gpudd-dynamic g18v3-sg9-subset02 subset th ads 问题 背景
_Case Study**2024-7-20**gpudd-dynamic_.md|L9-L41|coredump 模型 监控 tensorrt 日志 上线 gpu pod core soc
_Case Study**2024-7-20**gpudd-dynamic_.md|L42-L51|编译 模型 发布 serving tensorrt guardian 日志 gpu qa core
_Case Study**2024-7-20**gpudd-dynamic_.md|L52-L77|predictor 模型 trt tensorrt bthread core target sample engine plan
_Case Study**2024-7-20**gpudd-dynamic_.md|L78-L97|编译 模型 trt 监控 guardian 日志 内存 todo eta pic
_Case Study**2025-2-7**search-gpusse-dynamic_.md|L1-L8|模型 trt 发布 gpu ss 版本 search-gpusse-dynamic pod rollback 问题
_Case Study**2025-2-7**search-gpusse-dynamic_.md|L9-L19|predictor 模型 trt 发布 日志 上线 版本 trt10 master fail
_Case Study**2026-12-29_ChatBot错误调用导致ZooKeeper 集群高负载.md|L1-L24|ps cpu ss ego zk session chatbot incident sre newprocess
\_Case Study**2026-12-29_ChatBot错误调用导致ZooKeeper 集群高负载.md|L25-L28|cpu 资源 ss ego zk session chatbot 根因 分析 用于
\_Case Study**2026-12-29_ChatBot错误调用导致ZooKeeper 集群高负载.md|L29-L32|ps 监控 ss zk session watch get qps 现象 描述
\_Case Study**2026-12-29_ChatBot错误调用导致ZooKeeper 集群高负载.md|L33-L44|wc ego-predictor predictor ego-predictor-client-go sdk newclient zk service watcher client
\_Case Study**2026-12-29_ChatBot错误调用导致ZooKeeper 集群高负载.md|L45-L83|wc 资源 ss code demo chatbot go func handlerequest ctx
\_Case Study**2026-12-29_ChatBot错误调用导致ZooKeeper 集群高负载.md|L84-L114|wc chatbot hotfix client server sdk demo ego newclient done
\_EgoV4_pure C** Custom protocol.md|L11-L16|版本 rpc protobuf egov4 version 兼容 升级 协议 平滑 重要
\_EgoV4_pure C** Custom protocol.md|L17-L22|淘汰 内存 rpc egov4 iobuf append_user_data nshead zero copy ego
\_EgoV4_pure C** Custom protocol.md|L23-L30|cpu 带宽 egov4 server keys index key uint64 uint8 客户端
\_EgoV4_pure C** Custom protocol.md|L31-L36|predictor 模型 egopredictor usage egov4 client channel demo 用户 其实
\_EgoV4_pure C** Custom protocol.md|L37-L44|ps cpu ss stress test pb rt protocol method client
\_EgoV4_pure C** Custom protocol.md|L45-L48|ps 监控 custom protocol echo brpc status wrapper qps latency
\_EgoV5_pure C\_\_ Custom protocol_Todo_.md|L25-L28|dense tensor interface 只有 输入 请求 直接 暴露 接口 尽可能减少
_TD_ Ego Generative Sample Format.md|L9-L23|样本 sparse 特征 dense feature ego parquet txt protobuf request
*TD*强化学习.md|L1-L28|模型 ps 同步 参数 sparse feature feature*tag dnn ego sub_model
\_TechDocs_Refactor of embeddings.md|L1-L14|模型 slot 延迟 sparse 任务 吞吐 landingtable v1v2 cas v2
\_TechDocs_Refactor of embeddings.md|L15-L20|dense shared input item v3 request fill req 合并 冗余
\_TechDocs_Refactor of embeddings.md|L21-L32|slot sparse sparseslot custom v3 unordered_map feautre req 处理 细节
\_TechDocs_Refactor of embeddings.md|L33-L42|trt emb embedding minibatch 内存 xla batch buffer tensor mini
\_TechDocs_Refactor of embeddings.md|L49-L52|chd code 遗留 代码 清理 考虑 支持 所有 标注 部分
\_TechDocs_Refactor of embeddings.md|L55-L72|编译 trt emb embedding sparse gpu dense 内存 xla pooling
\_TechDocs_Refactor of embeddings.md|L73-L90|emb feature ss batch user items input shape inputdim fill
\_TechDocs_Refactor of embeddings.md|L91-L100|编译 sparse dense int64 double dt_type fill float dt type
\_TechDocs_Refactor of embeddings.md|L101-L104|向量 user req item 预估 支持 一些 算法 需求 我们
\_TechDocs_Refactor of embeddings.md|L105-L106|向量 slot emb embedding sparse dense 内存 projects status look
\_deprecate_DSSM model version consistency.md|L9-L19|get_model service code there two function model_name model_version point latest
\_deprecate_DSSM model version consistency.md|L20-L27|release destruct old model names like model_name model_version atomic counter
\_deprecate_DSSM model version consistency.md|L28-L35|point model should multi version control set multi_version true json
\_deprecate_Model Publish to USS for 0_4.md|L7-L22|presently us s3 develop s3_sync sh get limit_model_cty env some
\_deprecate_Model Publish to USS for 0_4.md|L23-L30|publish ss hdfs uss testing solution cmd developing register cluster
\_deprecated_GPU test.md|L1-L21|gpu ss want know something test please refer docker run
\_deprecated_Lyra平台使用.md|L3-L6|ego-predictor predictor ps lyra ofgzg 申请 权限 参照 最后 一步
\_deprecated_Lyra平台使用.md|L7-L14|ego-predictor predictor 模型 terminal lyra tenant application service wyatt guo
\_deprecated_Lyra平台使用.md|L15-L18|monitoring predictor ps 监控 grafana egopredictor infra sz htscqnyvz egopredictor-basis-lyra
\_deprecated_Lyra平台使用.md|L19-L23|ps 日志 carbon log log-search date-time type rel relativetime unit
\_deprecated_Use as lib.md|L1-L4|provide platform predict service deprecated up static library provides ability
\_deprecated_Use as lib.md|L5-L19|compile hdfs download please verify up_lib v0 tgz path r2
\_deprecated_Use as lib.md|L20-L31|compile release hdfs run example hadoop fs cat r2 projects
\_deprecated_Use as lib.md|L34-L37|up globalinit static method sets environment variables only call once
\_deprecated_Use as lib.md|L38-L43|predictor emb ss up modelpredictor class public member functions
\_deprecated_Use as lib.md|L44-L49|ss bool init const std string model_path loads model stored
\_deprecated_Use as lib.md|L50-L57|ss bool init_async const std string model_path asynchronously load model
\_deprecated_Use as lib.md|L58-L65|emb ss bool wait_for_init size_t time_out used conjunction init_async member
\_deprecated_Use as lib.md|L66-L73|feature ss bool predict const srec proto up predictrequestv3 request
\_deprecated_Use as lib.md|L74-L77|predictor example code using up static library include interface model_predictor
\_deprecated_Use as lib.md|L78-L81|setting environment variables call static method begin program set
\_deprecated_Use as lib.md|L82-L93|predictor initialization each modelpredictor object only initialized once load one
\_deprecated_Use as lib.md|L94-L97|prediction input srec proto up predictrequestv3 object make predictions save
\_deprecated_Use as lib.md|L98-L101|compile ss proto message definition compiled protobuf
\_emb only_2025-10-16.md|L3-L39|ps emb cpu a30 gpu ss 版本 input tensor concat
\_emb only_2025-10-16.md|L40-L76|ps emb a30 gpu input tensor concat qps latency gputl
\_fp16 accuracy debug*半精度损失追查.md|L9-L26|模型 serving 半精度 日志 onnx gpu 版本 weight trunct fp32-
*fp16 accuracy debug*半精度损失追查.md|L27-L44|ps trt tensorrt onnx fp16 score accuracy debug github nvidia
*fp16 accuracy debug*半精度损失追查.md|L45-L48|onnx mark output build find accuracy problem op engine very
*fp16 accuracy debug*半精度损失追查.md|L49-L54|模型 tensorrt onnx onnxruntime validate diff sample input tensor output
*fp16 accuracy debug*半精度损失追查.md|L55-L75|模型 训练 推理 半精度 离线训练 op fp16 inf nan min
_hstu_l40s ** l4 ** A30压测.md|L1-L37|l40s 模型 ps l4 a30 summary hstu bf16 qps wiki
\_hstu_l40s ** l4 ** A30压测.md|L40-L41|ps l4 cpu gpu qps laetncy cores util dev_mem_copy_util latency
\_hstu_l40s ** l4 ** A30压测.md|L42-L44|l40s ps l4 cpu gpu qps laetncy cores util dev_mem_copy_util
\_hstu_l40s ** l4 ** A30压测.md|L47-L48|ps l4 cpu gpu qps laetncy cores util dev_mem_copy_util latency
\_hstu_l40s ** l4 ** A30压测.md|L49-L51|l40s ps l4 cpu gpu qps laetncy cores util dev_mem_copy_util
\_hstu_l40s ** l4 ** A30压测.md|L52-L62|l40s portal presstest ps l4 serving a30 gpu dense ego-portal
\_test_ push quantization offload.md|L1-L18|deepctr 模型 ps emb 半精度 benchmark checkpoint ss online shard
_test_ push quantization offload.md|L19-L25|monitoring ps 监控 cpu onlineps 延迟 grafana push float mix
_test_ push quantization offload.md|L26-L37|deepctr 模型 checkpoint hdfs int8 index controller-uat-test online r2 projects
_test_ push quantization offload.md|L38-L52|deepctr 模型 ps emb benchmark checkpoint ss int8 online shard
_test_ push quantization offload.md|L53-L59|monitoring ps 监控 cpu onlineps 延迟 grafana push float int8
_test_ push quantization offload.md|L62-L67|monitoring ps onlineps grafana search sg search-sg7-replica-0 infra sz szmn18svk
_test_ push quantization offload.md|L68-L72|monitoring ps onlineps grafana hawkinga hawkinga-replica0 infra sz szmn18svk ego-onlineps-jian-kong-soc
_v1_2 noconcat_2025-10-16.md|L13-L14|ps a30 gpu nocat qps latency gputl mcutl smocc tensor
\_v1_2 noconcat_2025-10-16.md|L15-L16|l40s ps l4 gpu nocat qps latency gputl mcutl gract
\_v1_2 noconcat_2025-10-16.md|L17-L18|ps l4 gpu nocat qps latency gputl mcutl smocc tensor
\_v1_2 noconcat_2025-10-16.md|L19-L21|ps a30 gpu nocat qps latency gputl mcutl smocc tensor
\_video_ Convert from TN Model to EGO Plain TXT.md|L7-L12|emb embedding sparse param introduction tn*model_file_path path embeddings tn model
\_video* Convert from TN Model to EGO Plain TXT.md|L13-L16|hdfs start training job ego plain txt files path corresponds
*上线规范\_online release guide v2.md|L3-L12|predictor ps release egopredictor deploy lyra merge master tag branch
*上线规范*online release guide v2.md|L17-L32|trt tensorrt scale one canary target live service lyra platform
*上线规范*online release guide v2.md|L35-L40|ss pay attention seatalk alert canary instance load some model
*上线规范*online release guide v2.md|L41-L50|monitoring predictor ps grafana egopredictor check monitor url infra sz
*上线规范*online release guide v2.md|L53-L60|monitoring predictor ps grafana egopredictor pay attention seatalk alert check
*上线规范*online release guide.md|L3-L12|predictor ps release deploy gitlab-ci cd merge master tag branch
*上线规范*online release guide.md|L15-L18|release liveish k8s platform livish usually only one instance just
*上线规范*online release guide.md|L23-L28|ss pay attention seatalk alert canary instance load some model
*上线规范*online release guide.md|L29-L34|monitoring predictor ps grafana sparse egopredictor check monitor infra sz
*上线规范*online release guide.md|L37-L44|monitoring predictor ps grafana sparse egopredictor pay attention seatalk alert
*上线规范*online release guide.md|L47-L52|release ss depoying script run canary deploy some one fail
accelerate ps load_checkpoint in the release model pipeline.md|L1-L6|predictor ps release checkpoint egopredictor current model pipeline troubles there
accelerate ps load_checkpoint in the release model pipeline.md|L7-L17|ego-learner release feature updated model pipeline optimizations activate should manually
add_slot_optimizers.md|L10-L21|ps slot emb embedding sparse feature ego add_slot_optimizers slots extra_optimizers
auto mixed precision benchmark.md|L5-L25|ps benchmark dd_din model model_path git garena ego-public ego-api-v1 tree
auto mixed precision benchmark.md|L26-L43|ps emb benchmark cart_feat model_path git garena ego-public ego-api-v1 tree
batch 512vs1024 \_PDP*.md|L1-L12|ps cpu gpu feature summary round batch size ego ranker
batch 512vs1024 _PDP_.md|L17-L19|ps cpu gpu feature result batch size ego ranker qps
batch 512vs1024 _PDP_.md|L20-L29|gpu settings gpu*pdp_l2unify_mhg_lite_fix my ph setup round
batch 512vs1024 \_PDP*.md|L32-L41|ps cpu gpu feature result trimming request items batch size
batch 512vs1024 _PDP_.md|L42-L58|gpu settings model list gpu*pdp_ltr_ns_index gpu_pdp_multilabel_vc_search_cate_ship_main gpu_pdp_vtt_unify_v3 tw gpu_pdp_l2unify_mhg_lite_fix ph
batch 512vs1024 \_PDP*.md|L61-L88|gpu settings experiment only run baseline model each countries conduct
batch 512vs1024 _PDP_.md|L89-L104|monitoring ps grafana result low ego load ranker infra sz
batch 512vs1024 _PDP_.md|L105-L112|cpu gpu summary usage slightly decrease increase ego batch size
batch 512vs1024 _PDP_.md|L113-L122|monitoring ps cpu grafana experiment infra sz goto p1cduwtiz orgid
batch 512vs1024 _PDP_.md|L123-L126|ps summary ego ranker fse loads comparable batch size higher
batch 512vs1024压测对比*Cart场景*.md|L1-L10|ps cpu ss summary metric definitions latency p99 ms rank
batch 512vs1024压测对比*Cart场景*.md|L11-L26|cpu a30 gpu cores cart dump gpu*cart_sub_region_unify gpu_cart_fgv6d3_mmoe_unify_din_f1_ego1 gpu_cart_multi_cgc_lite gpu_cart_mask_unify_egov1
batch 512vs1024压测对比\_Cart场景*.md|L27-L31|ps cpu gpu server batch qps p99 ms 压测端 运行
batch 512vs1024压测对比*Cart场景*.md|L32-L37|monitoring ps grafana release ranker recording period link infra sz
batch 512vs1024压测对比*Cart场景*.md|L40-L53|ps feature previous recordings ranker load qps ego latency rank
batch 512vs1024压测对比*Cart场景*.md|L54-L58|ps cpu gpu server batch qps p99 ms 压测 记录时间
batch 512vs1024压测对比*Cart场景*.md|L59-L62|monitoring ps grafana release ss ranker link infra sz w9gsvttiz
batch 512vs1024压测对比*Cart场景*.md|L65-L75|feature previous recordings ranker ego latency load fp fetcher
batch 512vs1024压测对比*DD场景*.md|L1-L19|ps cpu ss summary metric definitions latency p99 ms rank
batch 512vs1024压测对比*DD场景*.md|L20-L27|cpu a30 gpu cores dd dump gpu*dd_rank_id_masknet_restart gpu_dd_feav4_lt_din_ple_unify_pruning_v2 th 环境
batch 512vs1024压测对比\_DD场景*.md|L28-L35|ps cpu gpu batch server qps p99 ms 压测 出现
batch 512vs1024压测对比*DD场景*.md|L36-L41|monitoring ps grafana release ss ranker pm gmt infra sz
batch 512vs1024压测对比*DD场景*.md|L42-L55|ps feature previous recordings ranker load qps ego latency rank
batch 512vs1024压测对比*DD场景*.md|L56-L62|ps cpu gpu 吞吐 server batch qps p99 ms 压测端
batch 512vs1024压测对比*DD场景*.md|L63-L66|monitoring ps grafana release ss ranker pm gmt infra sz
batch 512vs1024压测对比*DD场景*.md|L69-L79|feature previous recordings ranker ego latency load fp fetcher
benchmark for multi*user_graph.md|L1-L4|background single user graph vs multi
benchmark for multi_user_graph.md|L5-L8|gpu ss stress test max capacity model gpu_dd_din_longterm_esmm_mpi br
benchmark for multi_user_graph.md|L9-L11|ps batch_size backet type single multi qps
benchmark for multi_user_graph.md|L12-L14|ps batch_size backet type single multi qps
benchmark for multi_user_graph.md|L15-L18|latency test one user items
benchmark for multi_user_graph.md|L19-L24|xla disable multi_user_graph cost ms timeline single_user_graph
benchmark for multi_user_graph.md|L25-L29|xla enable multi_user_graph cost ms timeline single_user_graph
best executor_GPU model*.md|L17-L31|模型 trt batch*size gpu mini_batch 吞吐 ss perf graph tool
best executor_GPU model*.md|L32-L48|模型 ps 配置 tensorrt gpu 吞吐 耗时 xla executor use*tensorrt
bf16和图优化.md|L9-L28|模型 显存 a30 吞吐 batch tf32 context bf16 压测 对比
bf16和图优化.md|L29-L36|ps 显存 资源 吞吐 peak qps 压测 评估 上述 估算
bf16和图优化.md|L37-L50|回滚 监控 资源 版本 线上 评估 优化 节省 前会 导致
bf16和图优化.md|L51-L55|模型 ps a30 overlap yanbin abel docs google spreadsheets vt3gsqyqpj6qim9d-dkbhezta4b122z9w0a5kwrgag
config module* ego-learner*yaml.md|L43-L109|evict eviction feature hdfs train config data_done_file default value ego
config module* ego-learner*yaml.md|L110-L117|round0 eval config part used dataset evaluation normally default ll
config module* ego-learner*yaml.md|L118-L124|eval train_config feature ss fea config part used evaluation task
config module* ego-learner*yaml.md|L125-L128|ps nsc config details please refer yamlconfig ego1 negative sample
config module* ego-learner*yaml.md|L129-L136|ss metric config min_num_samples_in_group number samples user less than doesn
config module* flags*txt.md|L3-L12|format flags txt cat intra_op_parallelism_threads inter_op_parallelism_threads placement by_shard log_device_placement false
config_adf.md|L11-L24|slot dense ego config_adf slots dense_name adf_dim adf_decay_rate use_adf true
config_default_nn_optimizer.md|L5-L17|ps dense ego config_default_nn_optimizer learning_rate ada_decay_rate ada_epsilon e-8 mom_decay_rate param
config_dump_tensor.md|L6-L14|batch_size config_dump_tensor with_sample_id param true requires tensor-shape dump tensors each
config_list_wise.md|L5-L16|ego config_list_wise list_len param fixed length item list case there
config_retrieve_slot_categories.md|L6-L16|ps slot emb embedding feature config_retrieve_slot_categories candidate_slots target_slot categories none
cuda graph优化.md|L3-L10|a30 gpu ss press test performed stress search dsrm models
cuda graph优化.md|L11-L20|eval release gpu ss online gray test grayed two instance
cuda graph优化.md|L21-L31|ps release gpu ss full released optimization scale down cards
cuda graph优化方案设计.md|L1-L12|同步 cpu 延迟 显存 gpu cuda graph nvidia 背景 介绍
cuda graph优化方案设计.md|L13-L23|训练 显存 gpu ss cuda graph tfbackend tfbackendrungpusinglethread backend run
cuda graph优化方案设计.md|L24-L62|模型 显存 ss cuda graph backend tfbackend tfsession warmup kernel
cudagraph 优化.md|L5-L11|模型 显存 内存 ss cudagraph cuda graph capture session dynamic
cudagraph 优化.md|L12-L20|cpu 显存 tf graph cuda launch node concat input capturing
cudagraph 优化.md|L21-L35|模型 显存 ss 版本 launch tf backend session cudagraphop output
cudagraph 优化.md|L36-L42|portal ps 训练 显存 sparse gpu ego-portal sparsednn_adf launch auc
cudagraph 优化.md|L43-L49|portal ps 训练 显存 gpu ego-portal 耗时 dsrm node launch
cudagraph 优化.md|L50-L54|portal coredump ps 显存 gpu ego-portal 耗时 sim base ab
cudagraph 优化.md|L55-L58|portal ps 显存 gpu ego-portal 耗时 dd_rr_mllm_s_v128th_th_v128th base ab job
cudagraph 改造细节.md|L1-L10|ps tf nv patch mr git garena yansheng zhang tensorflow-2
cudagraph 改造细节.md|L11-L14|编译 ps compile tf git garena ego tf-compile merge_requests new
cudagraph 改造细节.md|L15-L20|gpu xla nv patch tf device stream executor third_party diff
cudagraph 改造细节.md|L21-L22|coredump 内存 bug fix cuda graph capturing library function tf
cvr_v31_mc_no_br_place_pay_sg性能对比\_stable auc*.md|L1-L11|wc 训练 任务 内存 summary addbatch sync gb metric 引入
cvr*v31_mc_no_br_place_pay_sg性能对比\_stable auc*.md|L12-L27|portal ps 任务 ego-portal feature master fix-multi-data-path live-test training job
cvr*v31_mc_no_br_place_pay_sg性能对比\_stable auc*.md|L28-L43|portal wc ps 训练 任务 worker ego-portal 内存 耗时 live-test
cvr*v31_mc_no_br_place_pay_sg性能对比\_stable auc*.md|L44-L59|portal ps 任务 ego-portal addbatch live-test training job detail info
cvr*v31_mc_no_br_place_pay_sg性能对比\_stable auc*.md|L60-L74|portal ps 任务 ego-portal addbatch syncdata live-test training job detail
dd 粗排*混排 CPU VS GPU置换比测试.md|L3-L20|ps cpu a30 gpu ss t4 xla dd_rr_esmm_classic dd_rr_lw_v2 idbackend
dd 粗排*混排 CPU VS GPU置换比测试.md|L21-L49|ps cpu a30 gpu t4 xla dd*mix_rank_prm_l50_new_cardid_stat idbackend tf-xla batch
dd 粗排*混排 CPU VS GPU置换比测试.md|L50-L58|a30 t4 c3v3 core g18v4 batch 结论 粗排 线上 情况
deploy different sub-models across multi-bundles while using the same sparse table.md|L3-L6|ps publish must deploy sub-models sequentially ensuring previous deployment succeeds
different poolings in EGO V1*0.md|L3-L8|slot emb embedding sparse feature ss usage last example there
different poolings in EGO V1_0.md|L11-L17|slot emb embedding sparse feature ss usage last example there
different poolings in EGO V1_0.md|L20-L25|slot emb embedding sparse feature ss usage last example there
different poolings in EGO V1_0.md|L28-L34|slot emb embedding sparse feature ss usage last example there
disk cache function.md|L3-L15|sampleserver batch_size minibatch ss batchfea generated batchparsers saved depends much
disk cache function.md|L16-L27|ps sampleserver worker ss most steps similar batchfea received according
doing feature importance test in egotf.md|L4-L15|eval slot sparse ego-learner dense feature configuration egotf-dnn use_tf_backend false
doing feature importance test in egotf.md|L16-L26|eval slot sparse compile ego-learner dense feature configuration egotf use_tf_backend
dumptensor相关报错.md|L1-L3|sparse dense ss core copyvaluefrom dump tensor inputs label weight
dynamic shape.md|L1-L6|cpu onnx onnxruntime xla tf support dynamic shape inference does
dynamic shape.md|L7-L29|trt tensorrt gpu xla does support dynamic shape should use
dynamic shape优化和batch size调整.md|L5-L13|模型 a30 subset01 subset02 latency 线上 缩容 对比 观察 缩卡后
enable tf run with cuda graph tech design draft.md|L5-L17|内存 ss cuda graph launch stream tf session run capture
fp16 * big batch size.md|L7-L17|模型 tensorrt 样本 gpu fp16 gpu*dsrm_v5_1_nimg sample dat fp32 bug
fp16 * big batch size.md|L20-L25|模型 ps a30 吞吐 docs google spreadsheets ju*o7g99kqwmqklrxpz19g2m_z16shfckh-v0-f2xfy edit usp
fp16 * big batch size.md|L26-L38|回滚 上线 gpu 版本 fp32 fp16 ego gpu*dsrm_v5_5_1_nimg gpu_dsrm_v5_5_1_nimg_fp16 subset
fread* fwrite* pread_direct* non-direct** pwrite*direct* non-direct*速率盘点.md|L1-L8|cpu 磁盘 任务 耗时 fwrite gb write_threads_num bazel-bin core io_test
fread* fwrite* pread_direct* non-direct** pwrite*direct* non-direct*速率盘点.md|L9-L16|cpu 磁盘 任务 耗时 fwrite gb write_threads_num bazel-bin core io_test
fread* fwrite* pread_direct* non-direct** pwrite*direct* non-direct*速率盘点.md|L17-L24|cpu 磁盘 任务 耗时 pwrite gb o_direct false write_threads_num bazel-bin
fread* fwrite* pread_direct* non-direct** pwrite*direct* non-direct*速率盘点.md|L25-L32|cpu 磁盘 任务 耗时 pwrite gb o_direct false write_threads_num bazel-bin
fread* fwrite* pread_direct* non-direct** pwrite*direct* non-direct*速率盘点.md|L33-L40|cpu 磁盘 任务 耗时 direct_io pwrite gb write_threads_num o_direct true
fread* fwrite* pread_direct* non-direct** pwrite*direct* non-direct*速率盘点.md|L41-L48|cpu 磁盘 任务 耗时 direct_io pwrite gb write_threads_num o_direct true
fread* fwrite* pread_direct* non-direct** pwrite*direct* non-direct*速率盘点.md|L49-L56|cpu 磁盘 任务 耗时 fread gb read_threads_num bazel-bin core io_test
fread* fwrite* pread_direct* non-direct** pwrite*direct* non-direct*速率盘点.md|L57-L64|cpu 磁盘 任务 耗时 fread gb read_threads_num bazel-bin core io_test
fread* fwrite* pread_direct* non-direct** pwrite*direct* non-direct*速率盘点.md|L65-L72|cpu 磁盘 任务 耗时 pread mb read_threads_num o_direct false bazel-bin
fread* fwrite* pread_direct* non-direct** pwrite*direct* non-direct*速率盘点.md|L73-L80|cpu 磁盘 任务 耗时 pread gb read_threads_num o_direct false bazel-bin
fread* fwrite* pread_direct* non-direct** pwrite*direct* non-direct*速率盘点.md|L81-L88|cpu 磁盘 任务 耗时 direct_io pread gb read_threads_num o_direct true
fread* fwrite* pread_direct* non-direct** pwrite*direct* non-direct*速率盘点.md|L89-L96|cpu 磁盘 任务 耗时 direct_io pread gb read_threads_num o_direct true
fread* fwrite* pread_direct* non-direct** pwrite*direct* non-direct*速率盘点.md|L97-L101|cpu 磁盘 上线 内存 direct_io 结论 在读 场景 多线程 并行
further discussions.md|L3-L10|模型 ps 跨机房 e-g server az 副本 带权 每个 权重
further discussions.md|L11-L14|ps server az 一地 机房 问题 可能 横跨
further discussions.md|L15-L19|ps server e-g sg my 两地 机房 问题 横跨 当地
g10v6内存分配和限流保护优化.md|L3-L11|ps l4 gpu 内存 gpushopmy gpushop g10v6 pinned memory g18v3
g10v6内存分配和限流保护优化.md|L12-L37|monitoring predictor 模型 ps trt 监控 l4 grafana gpu egopredictor
get_dense_feature.md|L9-L23|dense feature dense_input get_dense_feature name feature_type dim use_nsc false dense_names
get_seq3d_slot.md|L5-L16|slot dense feature sum pooling inner_list_len_dense_name inner list inner_list_max_len fkey1
get_slots.md|L6-L29|slot sparse feature ss sparse_input get_slots name slots dims poolings
get_slots.md|L30-L44|slot sparse ss attentions input name should unique multiple tile-pooling
gnn_init.md|L1-L13|ego relationconfig self name str max_edges int e9 initial_key_num extra_label_num
gnn_init.md|L14-L26|evict ego gnn_init relations list relationconfig expire_time int evict_days str
gnn_sample.md|L1-L22|slot ego getrelationoption relation_name str to_slot int sample_method gnnsamplemethod by_timestamp
gnn_sample.md|L23-L29|batch_size ego getrelationoption get_dst_ids_nums only call function calling gnn_sample return
gnn_sample.md|L30-L36|batch_size ego getrelationoption get_timestamp only call function calling gnn_sample return
gnn_sample.md|L37-L53|slot dense feature ego gnn_sample src_ids_name str get_relations list getrelationoption
gnn_update.md|L1-L20|evict dense feature ego gnn_update src_ids_name str dst_ids_name relation_name weight_name
gpu pdp cvr多国家基线模型图优化.md|L18-L26|ps gpu peak qps model mode batch size throughput latency
gpu pdp多国家基线模型图优化.md|L16-L21|ps gpu t4 qps batch size throughput latency ms gpus
gpu pdp多国家基线模型图优化.md|L22-L38|模型 ps gpu qps vs subset latency 线上 收益 评估
gpu sguide上动态路由.md|L13-L23|模型 ps a30 gpu 资源 complete 可退 高峰 时候 我们
gpu video 模型图优化.md|L29-L39|模型 ps gpu qps batch size throughput latency ms gpus
gpu video 模型图优化.md|L40-L44|上线 latency v3m3 base v2m2 情况 对比 如下 优化 结果
gpu video图优化.md|L1-L7|模型 onnx gpu ss pass gpu_video_cvr_seq2 matmul_opt_combination concat matmul pattern
gpu video图优化.md|L8-L13|ps t4 docs google spreadsheets ygwtraegv4tzo3gwfj4ytyffj0fqvbvfvdlgsrxllr0 edit gid 离线 压测
gpu video图优化.md|L14-L25|模型 ps 监控 配置 上线 gpu t4 qps video 线上
gpu video图优化.md|L26-L28|上线 gpu t4 优化 结论 利用率 整体 下降 左右 缩容卡
gpu_dsrm_v6_2_business_pal 模型优化.md|L9-L12|ps a30 gpu ss ab peak qps model name version
gpu_dsrm_v6_2_business_pal 模型优化.md|L13-L23|ps a30 gpu qps subset 在线 结果 上图 看到 优化
gpu_ecom_click_marm_v1m8_opt 模型图优化.md|L9-L16|ps a30 gpu batch size model name version type peak
gpu_ecom_click_marm_v1m8_opt 模型图优化.md|L17-L27|monitoring predictor ps 监控 grafana 上线 gpu egopredictor infra sz
gpu_prerank2_rrm_id_v1_8 模型优化.md|L9-L12|ps a30 gpu ab peak qps model name version type
gpu_prerank2_rrm_id_v1_8 模型优化.md|L13-L25|模型 ps a30 gpu subset qps sg9-1 sg9-2 在线 结果
gpulivestream图优化.md|L1-L7|模型 trt ss pass remove_onehot onehot matmul gather loop_optimization h2d
gpulivestream图优化.md|L8-L13|ps t4 docs google spreadsheets ygwtraegv4tzo3gwfj4ytyffj0fqvbvfvdlgsrxllr0 edit gid 离线 压测
gpulivestream图优化.md|L14-L24|ps gpu t4 qps 线上 收益 评估 更新 前后 明显
gpushop优化.md|L23-L30|l4 gpu 内存 gpushopmy gpushop g10v6 server client 优化 背景
gpusse-us优化.md|L5-L10|模型 cpu 推理 gpu cuda graph list wise 优化 策略
gpusse-us优化.md|L11-L16|模型 ps a30 gpu ss gpusse-us listwise rt peak qps
gpusse-us优化.md|L17-L22|cpu 推理 gpu cuda graph lstm 灰度 对比 实例 加上
gpusse-us优化.md|L23-L30|ps cpu a30 gpu cuda graph lstm pod qps 压测
gpusse-us优化.md|L31-L34|ps a30 gpu peak qps 线上 评估 收益 缩容 卡后
gpusse-us优化.md|L35-L38|a30 buffer 最终 收益 暂时 按卡算 业务 剩余 反转 流量
gpusse-us优化.md|L39-L41|模型 a30 update 算法 剩余 反转 流量 推全 从线 观测
gr模型访问ps压测报告.md|L1-L14|模型 ps onlineps 延迟 a30 gpu 吞吐 conclusion onlineps-search-test a30gpu
gr模型访问ps压测报告.md|L17-L33|模型 ps 监控 gpu 吞吐 mix precision model ms rpc_replay
gr模型访问ps压测报告.md|L34-L45|模型 ps 监控 a30 gpu 吞吐 full precision model ms
guideline for self-debug.md|L7-L14|click offline training job personal failed task see crash step
guideline for self-debug.md|L15-L26|serving publish click online publishing job personal failed model ist
guideline for self-debug.md|L27-L35|ps analysis until now see step wrong failed sandbox job
guideline for self-debug.md|L36-L42|egotrain grafana check memory consumption click monitor over limit
half precision transfer performence.md|L3-L6|deepctr ss experiment settings performance difference between float bfloat16 transmission
half precision transfer performence.md|L9-L14|ss training curve using float bfloat16 almost same according algorithm
half precision transfer performence.md|L15-L18|ps cpu worker statistics float32 bfloat16 traffic tb reduce client
half precision transfer performence.md|L21-L26|ss training curve using float bfloat16 almost same according algorithm
half precision transfer performence.md|L27-L28|ps cpu worker statistics float32 bfloat16 traffic tb reduce client
how to utilise gdb tool in remote cluster.md|L1-L4|egotrain compile release recompile outputs core files released image doesn
how to utilise gdb tool in remote cluster.md|L7-L9|ego-train resubmit job new image wait crash core files generated
import_extra_dense_feature.md|L5-L12|dense feature ego import_extra_dense_feature name str feature_type featuretype dim int
import_extra_slots.md|L1-L11|slot emb embedding ego import_extra_slots slots dims param list import
map精排压测\_ple_train_v7_2t_drpt0_1_keras_reorg*.md|L3-L14|ps cpu item tf run ms graph p99 qps todo
map精排压测*ple_train_v7_2t_drpt0_1_keras_reorg*.md|L15-L19|ps cpu onnx graph item p99 ms qps 继续 往上
megatron模型并行调研.md|L1-L10|模型 ss megatron gpt modulespec transformer block spec dataclass layer
megatron模型并行调研.md|L11-L16|模型 emb 参数 显存 embedding ss model*provider megatron gpt pretrain_gpt
megatron模型并行调研.md|L17-L24|模型 参数 train megatron keras training py fit incomplete 框架
megatron模型并行调研.md|L25-L32|显存 tensor columnparallellinear rowparallellinear rank weight output gather all reduce
megatron模型并行调研.md|L33-L50|模型 sequence megatron tensor layout batchsize seqlength hiddensize input all-gather
megatron模型并行调研.md|L51-L60|模型 参数 pipeline stage transformer megatron pipeline-model-parallel-size layer num core
megatron模型并行调研.md|L69-L78|模型 gpu layer device device2 node 朴素 思路 不同 放在
megatron模型并行调研.md|L79-L97|训练 显存 内存 ss gpipe batch pipestream weight staleless micro-batch
megatron模型并行调研.md|L98-L110|同步 ss 版本 one-forward-one-backward f1b pipedream gpipe micro batch forward
megatron模型并行调研.md|L111-L130|模型 训练 同步 显存 内存 ss pipedream-flush megatron-lm staleness pipestream
megatron模型并行调研.md|L131-L149|ps 版本 zero bubble penghui qi f1b1 backward stage pipeline
megatron模型并行调研.md|L150-L163|ps 训练 显存 dualpipe deepseek v3 moe all-to-all computation communication
metric calc耗时优化.md|L1-L4|wc add_batch calculcatioin calculation collective reduce op 性能 瓶颈 分析
metric calc耗时优化.md|L5-L13|wc ps ego-train gpu mr git garena ego ego-train-v1 merge_requests
metric计算并行化改造.md|L7-L9|collectivecommunication metric alltoall reduce barrier 优化 改造 要点 异步 多个
metric计算并行化改造.md|L10-L15|wc ps ego-train tag collective mr git garena ego ego-train-v1
metric计算并行化改造.md|L16-L18|portal ps worker ego-portal ss video rank model base metirc
metric计算并行化改造.md|L19-L24|portal ps 监控 任务 ego-portal 耗时 video rank staytime_crsg_fusion_dnn metric
metric计算并行化改造.md|L25-L29|portal ps 训练 benchmark ego-portal 耗时 ego_benchmark_search-ranking-deep-cvr auc diff base
metric计算并行化改造.md|L30-L34|portal ps 训练 benchmark ego-portal 耗时 ego_benchmark_din auc diff base
metric计算并行化改造.md|L35-L39|portal ps 训练 benchmark ego-portal 耗时 ego_benchmark_sim auc diff base
metric计算并行化改造.md|L40-L43|portal ps 训练 benchmark ego-portal 耗时 ego_benchmark_dd_din_lt_mpi4_ge_id_light_gate auc diff base
metric计算并行化改造.md|L44-L48|portal ps 训练 benchmark ego-portal 耗时 ego_benchmark_dsrm auc diff base
metric计算并行化改造.md|L49-L50|portal ps 训练 benchmark ego-portal 耗时 ego_benchmark_listwise base ab live-test
mini ranker对外接口.md|L3-L12|配置 feature predictreques service_info context afp dump_feature_bits dump bit item
model agent分享.md|L1-L9|编译 模型 配置 任务 gpu 版本 modelagent s3 base log
model agent分享.md|L10-L13|predictor ps egopredictor model debug git garena ego blob master
model agent分享.md|L14-L26|predictor 模型 ps egopredictor docs google document hgwnz4kajghtdkqfzlczlrb41sjujrxienxvfxnye1c edit usp
model-wise lb gray release.md|L1-L6|predictor ps onlineps gpu onlinps-recommendationb services az sg9 sg10 sg8
model-wise lb gray release.md|L7-L23|monitoring ps onlineps grafana gpu ss recommendation-gpupdp cross-zone traffic monitor
model-wise lb gray release.md|L24-L26|ps gpu recommendation-gpupdp-dynamic service model-wise lb qps 我们 开启 看出
my机房xla推广进展及问题.md|L3-L6|模型 search project search_algo ctr cvr lijingyi mailto niabel sea
my机房xla推广进展及问题.md|L7-L10|xla ctr jim chen 部分 之前 离职 负责 对应 业务
my机房xla推广进展及问题.md|L11-L14|模型 gpu xla cvr guoliang zhou q3 部分 负责 对应
my机房xla推广进展及问题.md|L15-L22|portal 编译 白名单 模型 ps ego-portal xla search training job
my机房xla推广进展及问题.md|L23-L26|rcmd project rcmd_dd rcmd_model hang zhang mailto albert cheng kailun
my机房xla推广进展及问题.md|L27-L64|portal 模型 ps 训练 cpu 任务 gpu ego-portal 耗时 xla
my机房xla推广进展及问题.md|L65-L80|portal 模型 ps 任务 ego-portal 耗时 xla auc owner rr_pdp_unify_v1_l2_unify
my机房xla推广进展及问题.md|L81-L93|portal ps 训练 任务 ego-portal xla local_debug diff live-test training
non-live resources application.md|L1-L2|machines env machine type number non-live s1 gb mem cores
non-live resources application.md|L5-L8|background development egov1 already started expected research completed second half
non-live resources application.md|L9-L12|ps onlineps calculation logic take deployment complete set egov1 run
offline ps 部署基线.md|L3-L8|编译 ps 部署 docker ecp openapi token offline 流程 源代码
offline ps 部署基线.md|L9-L12|编译 配置 docker bazel 源代码 构建 镜像 完成 后会 可执行文件
offline ps 部署基线.md|L13-L16|ss ecp openapi token curl location request get bigcompute infra
offline ps 部署基线.md|L17-L48|部署 ss ecp openapi curl location request post bigcompute infra
offline ps 部署基线.md|L49-L58|ps 参数 日志 docker offline shell pod online 镜像 启动
online learning user guideline.md|L6-L9|kafka prepare online training data pipeline take recommendation team example
online learning user guideline.md|L12-L54|kafka converter ego-learner hdfs prepare correct configuration file example yaml
online learning user guideline.md|L55-L66|portal ps submit online learning job ego-openapi-v1 compared batch training
online learning user guideline.md|L67-L71|predictor egopredictor ss state transition preprocess real time running training
online ps 部署基线.md|L3-L8|编译 ps 部署 docker ecp openapi token online 流程 源代码
online ps 部署基线.md|L9-L12|编译 配置 docker bazel 源代码 构建 镜像 完成 后会 可执行文件
online ps 部署基线.md|L13-L16|ps ecp openapi token curl post user-information-center apis uic v2
online ps 部署基线.md|L17-L38|ps 配置 onlineps 参数 部署 ecp openapi curl kubernetes devops
online ps 部署基线.md|L39-L48|ps 参数 日志 docker online shell pod 镜像 启动 命令
onlineps-videoa 灰度.md|L1-L4|ps client pswrr qps fig psclient sg10 sg9 traffic 调整
onlineps-videoa 灰度.md|L5-L11|monitoring ps onlineps grafana 负载均衡 client pswrr fig psclient sg10
pad matmul on gpu-dd.md|L11-L14|ps trt a30 gpu ego model name version batch size
pad matmul on gpu-dd.md|L15-L30|ps 上线 gpu latency gpu_dd_cvr_l2_unify_ads_ph ph max usage offset qps
pad matmul on gpu-dd.md|L31-L39|a30 gpu 资源 qa gpu-dd-dynamic gpu-dd ads carl quota sre
performance comparison* O2 vs O3 compile config.md|L1-L3|portal deepctr ps cpu 任务 worker 资源 ego-portal ss 耗时
performance comparison* O2 vs O3 compile config.md|L4-L6|portal ps cpu 任务 worker 资源 ego-portal ss 耗时 din
performance comparison* O2 vs O3 compile config.md|L7-L9|portal ps cpu sparse 任务 worker 资源 ego-portal ss 耗时
performance comparison* O2 vs O3 compile config.md|L10-L11|portal ps cpu 任务 worker 资源 ego-portal ss 耗时 dsrm
performance comparison* O2 vs O3 compile config.md|L12-L13|portal ps cpu 任务 worker 资源 ego-portal ss 耗时 dd*din_lt_mpi4_ge_id_light_gate
performance comparison* O2 vs O3 compile config.md|L14-L15|portal ps cpu 任务 worker 资源 ego-portal ss 耗时 sim
predictor 支持online learning模型更新.md|L5-L31|模型 ps onlineps 参数 split nn tf table summary tensor
previous IO benchmark.md|L3-L4|portal 模型 ps cpu 任务 worker ego-portal ss core metrics
profiling SampleServer.md|L7-L40|磁盘 sampleserver 内存 perf dynamic*cast malloc_consolidate unlink_chunk isra memmove_avx_unaligned_erms strcmp_avx2
ps load_checkpoint报错\_err_msg_Load model got exception_nn slice_594* invalid** error*code_104*.md|L5-L7|ckpt 模型 配置 训练 参数 ego-learner yaml filter nn true
ps performance related factors.md|L3-L6|ps onlineps request data size influences latency test done onlineps-recommentdationc
ps performance related factors.md|L7-L11|ps emb onlineps server shard number influences latency test done
python worker.md|L1-L4|worker ss python train job running k8s sample service written
python worker.md|L7-L15|deepctr ps worker adapt model demo file git garena ego-public
python worker.md|L16-L23|ego-train publish worker run model cluster official version hasn published
python worker.md|L24-L32|deepctr ps worker train debug model local machine python fly
python worker.md|L33-L36|ps running demo shown above used mocked more connect one
python worker.md|L37-L38|ps parameter*server ss manually start cluster shard_num run docker envyansheng
python worker.md|L39-L43|wc deepctr ps worker ss connect cluster return training docker
python worker.md|L44-L47|ego-learner minibatch use limit_minibatch_num limit many batches sample server read
python worker.md|L50-L54|ps learning rate schedule change dynamically instead use too many
python worker.md|L55-L59|ss use metric result default learner end_round returned json string
python worker.md|L60-L74|slot emb embedding fetch gradient training want step must call
python worker.md|L75-L76|grafana ss report user self defined metric def trainer_run global
python worker.md|L77-L79|ps evict ss trigger dump manually def trainer_run global rounds
python worker.md|L80-L82|ps ss get model stat info def trainer_run global rounds
python worker.md|L85-L88|训练 ss ego learner python class wrapped expose interface begin_pass
python worker.md|L89-L93|slot emb embedding py_ego_core slotcategory slot_category print 描述 信息 当想
python worker.md|L94-L99|模型 slot emb 参数 embedding py_ego_core batchfea python learner get_next_batch
rdma benchmark.md|L13-L14|v1 throughput-out through-in avg-latency brpc perf tcp mb ms rdma
rdma服务发现联调.md|L5-L9|train_threads ps 配置 训练 cpu 显存 半精度 任务 worker gpu
rdma服务发现联调.md|L12-L16|train_threads ps 配置 训练 cpu 显存 半精度 任务 worker gpu
rdma服务发现联调.md|L19-L23|train_threads ps 配置 训练 cpu 显存 半精度 任务 worker gpu
rdma服务发现联调.md|L26-L33|train_threads ps 配置 训练 cpu 显存 半精度 任务 worker gpu
rdma服务发现联调.md|L36-L39|train_threads ps 配置 训练 cpu 显存 半精度 任务 worker gpu
rdma服务发现联调.md|L40-L46|任务 redis ttl scale expire 服务 发现 联调 功能 节点
rdma服务发现联调.md|L47-L57|round0 监控 日志 redis rdma staticinit dynamicinit total brpc 问题
rdma问题整理.md|L7-L10|train_threads ps 参数 worker shard pod ecn pfc brpc rdma
rdma问题整理.md|L11-L16|ps worker gpu 资源 ecn my rq size brpc srq
rdma问题整理.md|L17-L28|ps 资源 ss ecn zhuanlan zhihu rdma lossless qp brpc
rdma问题整理.md|L29-L40|ps 训练 worker offlineps ss ecn explicit congestion notification rdma
replace_gradient.md|L10-L22|slot sparse ss ego replace_gradient input_tensor tensor_to_replace_gradient grad_tensor param target
set_layers_optimizer.md|L7-L23|ps ego set_layers_optimizer optimizer layers_prefix none param nn dim config
ss in worker_do sample convert in worker pod*.md|L11-L14|编译 worker ss sample server pod 方案设计 采用 逻辑 方式
ss in worker*do sample convert in worker pod*.md|L15-L20|ps ego-train git garena ego ego-train-v1 merge*requests diffs ego-common merge_requ
ss in worker_do sample convert in worker pod*.md|L21-L31|发布 ego-train dev harbor shopeemobile mlp-ego ego-train-runtime v1 dev-4a8fa78d-tf1-sg-20241031035840 dev-4a8fa78d-tf1-u
ss in worker*do sample convert in worker pod*.md|L32-L35|cpu a30 gpu ss cost 测试 结论 整体 平均 分配
ss in worker*do sample convert in worker pod*.md|L38-L42|portal 模型 ps 配置 训练 worker gpu ego-portal ss rcmd*model
ss in worker_do sample convert in worker pod*.md|L43-L50|portal round0 ps 监控 round1 训练 cpu worker gpu 资源
ss in worker*do sample convert in worker pod*.md|L51-L63|portal ps 训练 cpu worker gpu 资源 ego-portal ss vedio
ss in worker*do sample convert in worker pod*.md|L64-L67|portal ps cpu worker gpu dense 资源 ego-portal ss rcmd
ss in worker优化.md|L19-L29|worker 内存 ss oom pod sample server pros cons 方案
ss in worker优化.md|L30-L47|wc 编译 ps 日志 ego-train worker ss sample server pros
ss in worker优化.md|L50-L54|portal 模型 ps 训练 worker 资源 ego-portal ss dsrm model
ss in worker优化.md|L55-L59|portal round0 模型 ps 配置 训练 cpu ego-portal listwise model
ss in worker优化.md|L60-L64|portal 模型 ps 配置 训练 cpu worker ego-portal ss 耗时
ss in worker优化.md|L65-L69|portal 模型 ps 配置 cpu worker benchmark 资源 ego-portal ss
ss in worker优化.md|L70-L72|portal ps cpu benchmark gpu ego-portal ego*speed_benchmark_dd_din_gpu base ab live-test
ss in worker优化.md|L73-L75|portal ps gpu ego-portal pdp_mix_org_ads_l2_quarter_warm_other base ab training job detail
ss in worker优化.md|L76-L77|portal ps cpu gpu ego-portal game_ads_ctr_v1_unify_gpu_other base ab training job
ss pooling benchmark comparison.md|L3-L6|portal deepctr ps ego-portal job live-test training detail nobreadcrumb tab
ss pooling benchmark comparison.md|L9-L12|portal deepctr ps ego-portal job live-test training detail nobreadcrumb tab
ss pooling benchmark comparison.md|L13-L16|portal ps ego-portal din job live-test training detail nobreadcrumb tab
ss pooling benchmark comparison.md|L17-L20|portal ps sparse ego-portal sparse_dnn_adf job live-test training detail nobreadcrumb
ss_worker pooling gpu perf comparison.md|L1-L10|round0 ps round1 cpu worker gpu ss din model mock
ss_worker pooling gpu perf comparison.md|L11-L15|ps a30 worker gpu t4 v100 vs pooling mlperf dell
streaming VQ ego侧改造设计方案.md|L1-L71|cpu gpu xla incomplete custom op complete kernel global train_step
streaming VQ ego侧改造设计方案.md|L72-L79|ps ref streaming vq real-time indexing large-scale recommendation vector quantization
streaming VQ ego侧改造设计方案.md|L80-L83|模型 ps 训练 emb tf op custom_ops vq item_emb codebook
streaming VQ ego侧改造设计方案.md|L84-L110|portal ps 训练 同步 参数 任务 vq server ego codebook
streaming VQ ego侧改造设计方案.md|L111-L114|checkpoint gnn server codebook cluster dump job vq load 保存
streaming VQ ego侧改造设计方案.md|L115-L136|ps 配置 kafka vespa pages viewpage action pageid dump min
streaming VQ ego侧改造设计方案.md|L147-L157|eval 特征 dense ss candidate round forward trainable impression 索引
streaming VQ ego侧改造设计方案.md|L158-L164|emb 推理 embedding 部署 user tower top-k vespa ego 上游
tf2_15 gpu_trt10_8_cuda12_8优化.md|L1-L10|predictor trt cpu gpu tf tf2 grappler remapping bug cuda
tf2_15 gpu_trt10_8_cuda12_8优化.md|L23-L29|a30 gpu gpugame-my sg my 优化 缩容卡 汇总 收益 总共
timeline-map精排模型.md|L1-L8|ps 参数 ss 耗时 xla tf mkl ms mklsoftmax sketch2sky
timeline-map精排模型.md|L9-L14|参数 耗时 xla tf mkl export tf_disable_mkl ms 默认 关闭
timeline-map精排模型.md|L23-L27|模型 todo mkl 压测 一下 线上 效果 什么样 优化
triton server测试.md|L7-L16|ps cpu gpu 吞吐 内存 triton sdk rpc qps items
triton server测试.md|L17-L26|predictor ps gpu egopredictor 吞吐 triton sdk api server perf_analyzer
triton server测试.md|L29-L39|gpu triton sdk rpc concurrency throughput infer sec p99 latency
triton server测试.md|L40-L45|ps gpu triton sdk api rpc latency p99 ms qps
triton server测试.md|L46-L49|predictor ps gpu egopredictor perf_graph th percentile time ms qps
triton server测试.md|L52-L61|gpu triton sdk rpc throughput infer sec p99 latency usec
triton server测试.md|L62-L67|ps gpu 吞吐 triton sdk api rpc latency qps ms
triton server测试.md|L68-L71|predictor ps gpu egopredictor perf_graph th percentile time ms qps
triton server测试.md|L74-L79|gpu triton sdk rpc client throughput infer sec p99 latency
triton server测试.md|L80-L85|ps gpu 吞吐 triton sdk api rpc latency qps ms
triton server测试.md|L86-L89|predictor ps gpu egopredictor perf_graph th percentile time ms qps
triton server测试.md|L90-L99|predictor 模型 tensorrt 推理 egopredictor ss 耗时 triton kserver sdk
triton server测试.md|L100-L106|predictor 模型 egopredictor ss more ego tensor rpc triton sdk
trt 10*图优化.md|L1-L6|predictor trt tensorrt gpu egopredictor 版本 bug dram utilization executor
trt 10*图优化.md|L7-L12|gpu t4 gpu-video g17v2sg10s 推全 缩容 缩容后 很多 最后
trt 10*图优化.md|L17-L26|模型 a30 gpu 吞吐 ss 版本 gpu-sse latency 线下 单机
trt10*14升级优化.md|L1-L7|l4 gpu recommendation gpuvideorank-my video recommendation-gpuvideorank-my 优化 背景 基于 上述
trt_backend vs xla_backend vs tf_backend 性能对比.md|L5-L64|portal 模型 ps 任务 ego-portal order guarantee project tf_backend training
trt_backend vs xla_backend vs tf_backend 性能对比.md|L65-L208|portal 模型 ps 任务 ego-portal dsrm_v5_5_2_opt tf_backend training job detail
trt_backend vs xla_backend vs tf_backend 性能对比.md|L209-L364|portal 模型 ps 任务 ego-portal pdp cart cvr tf_backend training
trt_backend vs xla_backend vs tf_backend 性能对比.md|L367-L376|portal presstest 模型 ps trt serving ego-portal ss xla pdp
trt_backend vs xla_backend vs tf_backend 性能对比.md|L377-L383|模型 trt xla conclusion tensorflow train graph frozen cuda optimize
use tf print to debug release fail.md|L5-L8|deepctr ps ss instructions use demo model example find all
use tf print to debug release fail.md|L9-L12|deepctr modify model file add ego tf_enable_debug true example deepctr_model
use tf print to debug release fail.md|L13-L14|deepctr hdfs put new model file hadoop fs deepctr_model py
use tf print to debug release fail.md|L15-L20|deepctr ss hdfs write export_initialize sh start online-export process would
use tf print to debug release fail.md|L23-L34|portal predictor ps worker release ego-portal diff result job finished
v0_1_0 FE tech design.md|L1-L39|checkpoint ss model page route design component no permission login
validate sample and request.md|L1-L27|参数 样本 特征 feature ss fulltrace request_id sample dat sample_id
validate sample and request.md|L28-L32|fulltrace python json 分析 返回 结果 脚本 文件 完善
video训练集群资源使用率提升.md|L1-L4|round0 worker 资源 ss period job v1 early exist 现状
video训练集群资源使用率提升.md|L7-L14|ps 样本 converter feature video proto git garena ai-engine-platform idl
video训练集群资源使用率提升.md|L15-L31|编译 ps converter cpp job python ego txt git garena
video训练集群资源使用率提升.md|L32-L37|converter src converters outputinstance 添加 目录 自己 仿照 实现 继承
video训练集群资源使用率提升.md|L38-L44|portal ps 训练 converter worker ego-portal ss cpp sample_converter python
wc - \_Caused by* java*io_IOException* java*net_SocketTimeoutException* 60000 millis timeout while waiting for channel to be ready for read*.md|L7-L11|配置 ego-learner 解决 方法 重试 关闭 检查 功能 新增 如下
xla mockps performance test.md|L1-L12|ps 训练 emb cpu 显存 样本 embedding ego-train a30 worker
xla mockps performance test.md|L15-L24|deepctr round0 round1 训练 cpu 参数 显存 batch_size gpu 内存
xla mockps performance test.md|L25-L36|portal 模型 ps 训练 参数 显存 benchmark release gpu ego-portal
xla mockps performance test.md|L37-L48|portal 模型 ps 训练 参数 benchmark gpu ego-portal pdp_vtt_unify_v3_tw batch
xla mockps performance test.md|L49-L54|portal 模型 ps 训练 cpu 参数 显存 benchmark gpu ego-portal
xla mockps performance test.md|L55-L57|deepctr 模型 训练 xla 测试 结论 除了 过于 简单 性能
xla优化\_tf2_16 MYDD的搜推集群优化.md|L5-L35|monitoring predictor ps 监控 grafana a30 gpu 资源 egopredictor dd
xla优化\_tf2_16.md|L13-L18|a30 gpu gpucart-us 推全后 集群 过载 空闲 评估 优化
xla优化rcmd粗排召回收益统计.md|L13-L26|portal 模型 ps ego-portal dd rollout rcmd bfeb bdd broughrank
xla优化rcmd粗排召回收益统计.md|L27-L32|portal 模型 ps ego-portal pdp my vn model model_management rr_pdp_unify_v1_l2_unify_r
xla优化rcmd粗排召回收益统计.md|L33-L36|portal 模型 ps 任务 ego-portal 耗时 xla owner rr_pdp_unify_v1_l2_unify qifan
xla优化search my机房收益统计记录.md|L3-L8|同步 cpu gpu 资源 xla ctr jim us my max
xla优化search my机房收益统计记录.md|L9-L14|portal 模型 ps 上线 gpu ego-portal xla cvr guoliang zhou
xla优化search my机房收益统计记录.md|L15-L22|portal 模型 ps 任务 ego-portal ss prerank prerank_ssl_org_ads_small_4_3 training periodrule
xla优化search my机房收益统计记录.md|L27-L31|资源 ctr max 除外 其他 业务 收益 较少 几个 方外
xla优化各业务线推广记录.md|L1-L4|ps xla search docs google document t7ugk2cwbejti7yf4o7ukfstay4brscwgx0j6daokwe edit usp sharing
xla优化各业务线推广记录.md|L5-L7|ps xla rcmd docs google document r8dstwfwho255cbbautcwhxc9s6cjjaeoe44-8pzzls edit usp sharing
上线讨论.md|L17-L23|predictor ps onlineps onlineps-videoa sg9 sg10 sg8 server 机房 两地
不同GPU机型性能测试.md|L1-L10|l40s l4 cpu 显存 a30 gpu 内存 nvlink intel xeon
不同GPU机型性能测试.md|L11-L12|l40s round0 train_threads 模型 round1 l4 配置 训练 cpu 参数
不同GPU机型性能测试.md|L13-L16|round0 train_threads h100 模型 round1 配置 训练 cpu 参数 显存
不同GPU机型性能测试.md|L19-L26|l40s deepctr h100 模型 l4 训练 a30 xla h20 v100
不同GPU机型性能测试.md|L27-L33|deepctr h100 模型 训练 xla dsrm_v5_5_dm_p5_atrst pdp_vtt_unify_v3_tw 实验 对于 计算
业务服务集群.md|L3-L6|predictor egopredictor customer-service-and-chatbot customer_service_and_chatbot chatbot_ds customer-service-and-chatbot-cus services egopredictor-cus-live-sg
业务服务集群.md|L7-L10|predictor ps egopredictor map mapsearch_ranking map-map services egopredictor-map-live-sg
业务服务集群.md|L11-L26|predictor egopredictor marketplace-mpi marketplace mpi mpi-bundle marketplace-mpi-bdl services egopredictor-bdl-live-sg mpi-ego-platform
业务服务集群.md|L27-L30|predictor egopredictor off-platform-ads off_platform_ads opa_algo off-platform-ads-opa services egopredictor-opa-live-sg
业务服务集群.md|L31-L66|predictor gpu egopredictor recommendation livestream_rank_offline recommendation-livestreamoffline services egopredictor-livestreamoffline-live-sg livestream recommendation-gpulivestream
业务服务集群.md|L67-L84|predictor gpu egopredictor ss search sguide search-gpusguide services up-gpusguide-live-sg search-gpusse-dynamic
业务服务集群.md|L85-L88|zk sg7 zk02-sg7-node01 rcmd-middleware zk02-sg7-node02 zk02-sg7-node03 节点 地址
以太网 vs rdma性能测试.md|L3-L6|train_threads ps 配置 训练 cpu 显存 半精度 任务 worker gpu
以太网 vs rdma性能测试.md|L7-L11|train_threads ps 配置 训练 cpu 显存 半精度 任务 worker gpu
以太网 vs rdma性能测试.md|L12-L15|eval 模型 训练 样本 带宽 ss dsrm_v552 dsrm_v70 round get_batch
以太网 vs rdma性能测试.md|L16-L19|train_threads ps 配置 训练 cpu 显存 半精度 任务 worker gpu
以太网 vs rdma性能测试.md|L20-L23|train_threads ps 配置 训练 cpu 显存 半精度 任务 worker gpu
以太网 vs rdma性能测试.md|L24-L35|ps gpu 带宽 gbps perf rdma brpc qperf 网卡 性能
以太网 vs rdma性能测试.md|L38-L41|train_threads ps 配置 训练 cpu 显存 半精度 任务 worker gpu
以太网 vs rdma性能测试.md|L44-L47|train_threads ps 配置 训练 cpu 显存 半精度 任务 worker gpu
以太网 vs rdma性能测试.md|L50-L59|train_threads ps 配置 训练 cpu 显存 半精度 任务 worker gpu
任务持续训练*但是metric指标不显示的问题.md|L3-L6|报错 原因 查看 是否 指标 上报 异常
任务持续训练*但是metric指标不显示的问题.md|L9-L15|样本 日志 auc illegal_count legal_count 关键字 过滤 查看 计算 指标
任务阻塞不训练的问题*任务没有显示AUC*.md|L7-L11|模型 配置 训练 磁盘 任务 ego-learner yaml 根据 上图 显示
使用conan * bazel构建c*c\_\_项目.md|L26-L49|ps compile release build_type os linux os_build arch x86_64 arch_build
关于ego集成pytorch的可能方案.md|L3-L7|模型 训练 gil pytorch ego grad tensor 单线程 执行 由于
关于ego集成pytorch的可能方案.md|L8-L11|训练 ss backend ego pytorch python tf session train learner
关于ego集成pytorch的可能方案.md|L12-L18|wc converter ss dataset sample server python pytorch tensor py
关于ego集成pytorch的可能方案.md|L19-L23|slot ss ego api get_slot placeholder pytorch pass round main
关于ego集成pytorch的可能方案.md|L24-L27|ps ego onlineround pytorch nn 子图 抽取 自动 线上 执行
关于ego集成pytorch的可能方案.md|L28-L44|模型 训练 推理 sparse 特征 megatron python pytorch pythonic fork
华佗2*自动调优灰度实验结果.md|L1-L4|模型 配置 训练 cpu gpu 带宽 ctr cvt 总结 搜索
华佗2*自动调优灰度实验结果.md|L7-L48|portal 模型 ps ego-portal ctr dd_rank_id_ma0_pf_mad_multimodal_deimp_id model model_management dd_rank_id_ma0_pf_mad_multimodal version
华佗2*自动调优灰度实验结果.md|L49-L88|portal 模型 ps ego-portal ss cvr rank*cvr_cross_scene_v1_lite8_test_id model model_management rank_cvr_cross_scene_v1
华佗2*自动调优灰度实验结果.md|L89-L154|portal 模型 ps evict ego-portal pdp rr*pdp_unify_madnn_v1-evict_id model model_management rr_pdp_unify_madnn
华佗2*自动调优灰度实验结果.md|L155-L189|portal 模型 ps ego-portal dd*rerank_prm_attn_v_broadcvr1d_id model model_management dd_rerank_prm version attn_v_broadcvr1d_zjz
华佗2*自动调优灰度实验结果.md|L192-L231|模型 训练 调优 cpu 任务 资源 ss 耗时 dsrm*v6_2_business_pal memory
华佗2*自动调优灰度实验结果.md|L232-L247|模型 ps 调优 cpu 任务 a30 worker 部署 资源 带宽
华佗二期*ego-auto-param-tune-kit.md|L3-L6|配置 cpu 任务 资源 内存 目的 针对 任意 检查 运行
华佗二期\_ego-auto-param-tune-kit.md|L7-L18|配置 任务 日志 资源 training egocontroller pod elastic store analysis
华佗二期\_ego-auto-param-tune-kit.md|L19-L65|监控 配置 任务 日志 analysis elastic store data_source kube-aip-training-us-us1-live tenant_name
华佗二期\_ego-auto-param-tune-kit.md|L66-L93|模型 配置 训练 调优 样本 任务 特征 耗时 analysis model_version
华佗二期\_ego-auto-param-tune-kit.md|L94-L100|配置 cpu 参数 任务 日志 资源 内存 egocontroller data_source tenant_name
单卡单模型VS单卡多模型.md|L3-L81|模型 ps gpu 吞吐 dd subset03 qps item batch size
单网卡双网卡训练速度性能对比.md|L3-L7|portal train_threads ps 配置 训练 cpu 半精度 任务 worker gpu
单网卡双网卡训练速度性能对比.md|L10-L13|portal train_threads ps 配置 训练 cpu 半精度 任务 worker gpu
取消WORKER_END_ROUND barrier实验.md|L5-L12|portal ps worker ego-portal 耗时 base steal worker_end_round barrier live-test
图优化.md|L1-L10|merge split partition fuse squeeze concat unsqueeze pad matmul input
图优化.md|L15-L20|gpu t4 model throughput gpu_pdp_l2unify_mhg_lite_fix ph my gpu_pdp_ego1_mix_ads_itemtype_seq_v1_all_target gpu_pdp_ego1_mix_ads_itemtype_seq_v1_all_target_ads gpu_pdp_ego1*
图优化.md|L21-L37|上线 gpu scale down usage model latency scaled xx cards
如何使用grafana或者tensorboard来展示tensor的变化*depreciated*作废*.md|L1-L9|grafana ego trace_tensor tf compat v1 tensor trace_name str trace_grad
如何追查同一个任务运行两次*数据量不一致的问题.md|L3-L7|样本 converter ss read bytes parsed sample package num ins
容灾*降级用户手册.md|L3-L38|predictor 部署 egopredictor zk naming zfs golang brpc grpc az
容灾*降级用户手册.md|L39-L59|predictor 模型 ps 部署 资源 egopredictor pod crash naming online
尝试优化pre*run_batch耗时及分析根因.md|L1-L4|任务 耗时 pre_run_batch tf_backend_run 问题 介绍 当前 执行 过程 阶段
尝试优化pre_run_batch耗时及分析根因.md|L5-L13|cpu sparse 日志 gpu 耗时 sparse_gpu_context dnn_gpu_context i0303 core train
尝试优化pre_run_batch耗时及分析根因.md|L14-L19|监控 sparse gpu 耗时 sparse_gpu_context dnn_gpu_context runbatch backend_run tf_backend_run ms
尝试优化pre_run_batch耗时及分析根因.md|L20-L34|max_context_per_device train_threads 模型 训练 显存 sparse max_session_per_device gpu 内存 ss
尝试优化pre_run_batch耗时及分析根因.md|L35-L41|portal 模型 ps 任务 ego-portal listwise_out_mixrank_score_v17_v2_rcmd_dd training job detail info
广告异常任务分析.md|L1-L2|round0 round1 训练 任务 耗时 summary eta egocontroller pushmodelperfmetric na
广告异常任务分析.md|L5-L22|round0 round1 训练 任务 日志 gpu ss 耗时 target auc
广告异常任务分析.md|L25-L39|wc round0 round1 配置 训练 cpu 任务 worker gpu ss
广告异常任务分析.md|L42-L48|sparse 任务 unique_fea_num device input fatal 异常现象 阻塞 因为 为空
广告异常任务分析.md|L51-L57|train_threads 训练 显存 任务 gpu ss xla context session 异常现象
开启Auto Mixed Precision并没有带来性能提升.md|L4-L8|deepctr 模型 dd_din_lt_cvr_joint_v1_br_newoa_as_align_br_align 实验
开启Auto Mixed Precision并没有带来性能提升.md|L9-L42|portal deepctr round0 ps round1 训练 任务 gpu ego-portal 耗时
开启Auto Mixed Precision并没有带来性能提升.md|L43-L85|portal deepctr round0 ps round1 训练 任务 gpu ego-portal 耗时
开启Auto Mixed Precision并没有带来性能提升.md|L86-L119|portal deepctr round0 ps round1 训练 任务 gpu ego-portal 耗时
开启Auto Mixed Precision并没有带来性能提升.md|L120-L153|portal deepctr round0 ps round1 训练 任务 gpu ego-portal 耗时
强化学习用户手册.md|L1-L18|模型 ps 同步 参数 sparse feature feature_tag dnn ego sub_model
性能对比*.md|L1-L8|portal ps 任务 ego-portal feature 耗时 master fix-multi-data-path training job
性能对比*.md|L9-L15|portal ps 任务 ego-portal 耗时 addbatch syncdata training job detail
性能对比*.md|L16-L23|portal ps 任务 ego-portal 耗时 addbatch training job detail info
性能对比*.md|L24-L30|portal ps 任务 ego-portal 耗时 addbatch syncdata training job detail
性能对比\_Tensorrt上开启fp16精度预测和开启tf32精度预测.md|L1-L13|portal deepctr presstest ps serving tensorrt ego-portal ss deepctr-v3 total
性能对比\_Tensorrt上开启fp16精度预测和开启tf32精度预测.md|L14-L27|portal presstest ps serving tensorrt ego-portal ss dd_din_lt_cvr_joint_v1_br_newoa_as_align_br_align total nn
性能对比\_Tensorrt上开启fp16精度预测和开启tf32精度预测.md|L28-L39|portal presstest ps serving tensorrt ego-portal ss dd_din_lt_esmm_mpi_softsim_cl_amg_dfrv_mnv4_d0_br total nn
性能对比\_stable auc*.md|L1-L8|portal ps 任务 ego-portal feature master fix-multi-data-path training job detail
性能对比*stable auc*.md|L9-L16|portal ps 任务 ego-portal training job detail info tab task
性能对比*stable auc*.md|L17-L24|portal ps 任务 ego-portal addbatch training job detail info tab
性能对比*stable auc*.md|L25-L31|portal ps 任务 ego-portal addbatch syncdata training job detail info
指标突然骤跌问题追查方向.md|L1-L4|ckpt evict 训练 feature ego flags txt enable*feature_evict false 查看
指标突然骤跌问题追查方向.md|L5-L31|egotrain 模型 ps 监控 训练 样本 grafana 特征 checkpoint ss
接入流程\_How to enroll*.md|L3-L14|egotrain predictor egopredictor related people ego manager yanbin zhao productor
接入流程*How to enroll*.md|L15-L20|样本 特征 feature ss bingxin fan sample generate store process
接入流程*How to enroll*.md|L21-L26|模型 训练 样本 特征 model train ego bill wu jingzhe
接入流程*How to enroll*.md|L27-L36|egotrain predictor 模型 发布 serving 训练 同步 任务 publish 部署
接入流程*How to enroll*.md|L37-L42|predictor 推理 资源 egopredictor ss inference resource ego k8s sre
推广ss优化镜像.md|L35-L53|cpu sampleserver 任务 worker gpu 耗时 h15m cp 基于 单个
推广ss优化镜像.md|L54-L57|monitoring eval 模型 ps grafana 任务 ego-train gpu infra sz
推荐g8v2机器使用优化1.md|L11-L33|模型 emb cpu guardian a30 部署 gpu 资源 耗时 dd
推荐g8v2部署优化2.md|L27-L34|gpu 资源 t4 buffer 优化 上述 集群 充分 利用 使得
推荐g8v2部署优化2.md|L35-L41|ps gpu 资源 t4 quota sre video space work admin
搜索利用GPU机器的CPU.md|L1-L10|cpu 推理 gpu 资源 ss result sse g18v3 影响 前提
搜索利用GPU机器的CPU.md|L11-L28|模型 cpu 推理 部署 gpu 资源 内存 ss tf2 numa
搜索利用GPU机器的CPU.md|L29-L31|cpu gpu g18v3 后续 计划 考虑 搜推 主流 机型 自定义
搜索问题梳理.md|L3-L26|模型 发布 训练 任务 worker 内存 ss my sg base
攒batch.md|L1-L18|dense model py layer tf dense*layer xxx output1 userinput1 output2
攒batch.md|L19-L37|ps emb sparse dense 内存 batch h2d pinned memory req1
攒batch.md|L38-L96|emb embedding sparse dense graph convert padding req batch pinned
支持MPI多Checkpoint的Online Learning与Serving自动更新方案.md|L1-L4|serving 训练 任务 checkpoint mpi ego online learning model 需求
支持MPI多Checkpoint的Online Learning与Serving自动更新方案.md|L5-L10|serving ego online learning train job model version real time
支持MPI多Checkpoint的Online Learning与Serving自动更新方案.md|L11-L14|任务 checkpoint mpi train job succeeded online learning 方案设计 接口
支持MPI多Checkpoint的Online Learning与Serving自动更新方案.md|L15-L20|serving train_config checkpoint online learning model config file days days_format
支持MPI多Checkpoint的Online Learning与Serving自动更新方案.md|L21-L27|checkpoint job online learning 相关 接口 查询 状态 产出 部分
检索单个worker上*每个round见过多少条数据.md|L3-L5|cpu gpu cat log grep finish run round idx round*idx
模型量化.md|L11-L16|整数 量化 数据 校准 浮点 回退 方案 某些 算子 没有
模型量化.md|L19-L38|ps graph transform tool fold_constants strip_unused_nodes round_weights bit int8 op
模型量化.md|L39-L41|ps github tensorflow tree master tools graph_transforms quantize_weights 参考资料
测试 * 灰度.md|L1-L35|predictor ps onlineps 跨机房 上线 部署 版本 controller uat live
测试用例.md|L6-L21|回滚 模型 ps evict worker 版本 controller import client prealloc-
测试用例.md|L22-L23|ps release checkpoint controller create online model load update redis
磁盘不足阻塞训练流程梳理.md|L1-L2|gpu free space tb num g21v4 g18v3 机器 机型
磁盘不足阻塞训练流程梳理.md|L3-L4|cpu free space gb core num c3v2 c3v3 机器 机型
磁盘不足阻塞训练流程梳理.md|L5-L6|portal ps 磁盘 样本 gpu ego-portal ss search rcmd scenario
磁盘不足阻塞训练流程梳理.md|L7-L11|模型 配置 训练 磁盘 样本 任务 特征 gpu ss ctr
磁盘不足阻塞训练流程梳理.md|L14-L18|模型 训练 磁盘 ss pass ctr cvr tb 限制 数据
磁盘不足阻塞训练流程梳理.md|L19-L25|模型 训练 cpu 磁盘 样本 sampleserver 任务 worker 带宽 ss
磁盘不足阻塞训练流程梳理.md|L28-L34|配置 调优 磁盘 样本 任务 ss pass batchdata tb g21v4
调度优化.md|L7-L14|模型 guardian frozen scheduler python idea 技术 方案 汲取 多次
调度优化.md|L15-L33|模型 ps 显存 部署 gpu qps subset base dd pdp
调研*通过SPDK tool来管理nvme磁盘.md|L147-L150|cpu 磁盘 spdk nvme 用户 驱动 上文 看出 系统 调用
调研*通过SPDK tool来管理nvme磁盘.md|L151-L164|cpu 磁盘 内存 spdk nvme reactor poller directio 介绍 基于
调研*通过SPDK tool来管理nvme磁盘.md|L165-L181|编译 ps ego-train gpu harbor shopeemobile mlp-ego ego-train-gpu-devel v3 tf1-sg-20240604164908
调研*通过SPDK tool来管理nvme磁盘.md|L182-L197|uio*pci_generic lib docker dev privilege nvme modprobe fio spdk-fio ld_preload
调研*通过SPDK tool来管理nvme磁盘.md|L198-L235|cpu 资源 directio gb cpus 测试 结果 充足 随机 顺序
跨机房流量优化 model-wise LB.md|L24-L64|模型 ps lb model channel shards models selectserver based kv
集群接入手册.md|L3-L15|ego-predictor predictor ps guardian gpu up server redis key git
集群接入手册.md|L16-L40|ego-predictor predictor 模型 ps 发布 guardian publish pod git garena
集群自动压测配置表.md|L3-L9|ps benchmark up bin workspace deploy auto_bench_script sh manual true
集群自动压测配置表.md|L10-L11|ps benchmark gpu subset qps recommendation-livestream idel-sg10 benchmark_hour qpschange qpslimit
