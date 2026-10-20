-- MySQL dump 10.13  Distrib 26.7.0, for macos15 (arm64)
--
-- Host: 127.0.0.1    Database: pases
-- ------------------------------------------------------
-- Server version	26.7.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--


--
-- Current Database: `pases`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `pases` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `pases`;

--
-- Table structure for table `detect_record`
--

DROP TABLE IF EXISTS `detect_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detect_record` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '检测主记录ID',
  `image_url` varchar(255) NOT NULL COMMENT '图片存储地址',
  `auditor_id` int DEFAULT NULL COMMENT '审核人ID，关联users.user_id',
  `audit_time` datetime DEFAULT NULL COMMENT '审核时间',
  `audit_remark` varchar(255) DEFAULT NULL COMMENT '审核备注',
  `detect_time` datetime DEFAULT NULL COMMENT '检测时间',
  `user_id` int DEFAULT NULL COMMENT '上传用户ID',
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='检测主记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detect_record`
--

LOCK TABLES `detect_record` WRITE;
/*!40000 ALTER TABLE `detect_record` DISABLE KEYS */;
INSERT INTO `detect_record` VALUES (1,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-23_17-17-29_141082.jpg',NULL,NULL,NULL,'2026-08-23 17:17:29',NULL,'2026-08-23 17:17:29'),(2,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-23_17-18-57_277329.jpg',NULL,NULL,NULL,'2026-08-23 17:18:57',NULL,'2026-08-23 17:18:57'),(3,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-23_17-26-43_406172.jpg',1,'2026-08-31 17:47:30','','2026-08-23 17:26:43',NULL,'2026-08-23 17:26:43'),(4,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-23_17-27-03_557918.jpg',NULL,NULL,NULL,'2026-08-23 17:27:03',NULL,'2026-08-23 17:27:03'),(5,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-23_17-28-21_160990.jpg',NULL,NULL,NULL,'2026-08-23 17:28:21',NULL,'2026-08-23 17:28:21'),(6,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-23_17-28-34_352079.jpg',NULL,NULL,NULL,'2026-08-23 17:28:34',NULL,'2026-08-23 17:28:34'),(7,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-23_17-28-47_483890.jpg',NULL,NULL,NULL,'2026-08-23 17:28:47',NULL,'2026-08-23 17:28:47'),(8,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-23_17-49-14_721109.jpg',NULL,NULL,NULL,'2026-08-23 17:49:14',1,'2026-08-23 17:49:14'),(9,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-23_17-51-53_646599.jpg',NULL,NULL,NULL,'2026-08-23 17:51:53',2,'2026-08-23 17:51:53'),(10,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-23_18-08-18_669868.jpg',NULL,NULL,NULL,'2026-08-23 18:08:18',2,'2026-08-23 18:08:18'),(11,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-23_18-10-03_290115.jpg',NULL,NULL,NULL,'2026-08-23 18:10:03',2,'2026-08-23 18:10:03'),(12,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-23_18-17-24_912567.jpg',NULL,NULL,NULL,'2026-08-23 18:17:24',2,'2026-08-23 18:17:24'),(13,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-23_18-17-45_602693.jpg',NULL,NULL,NULL,'2026-08-23 18:17:45',2,'2026-08-23 18:17:45'),(18,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-23_18-27-49_863361.jpg',NULL,NULL,NULL,'2026-08-23 18:27:49',2,'2026-08-23 18:27:49'),(19,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_12-47-45_112401.jpg',NULL,NULL,NULL,'2026-08-24 12:47:45',2,'2026-08-24 12:47:45'),(20,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_12-47-55_514390.jpg',NULL,NULL,NULL,'2026-08-24 12:47:55',2,'2026-08-24 12:47:55'),(21,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_12-48-06_034356.jpg',NULL,NULL,NULL,'2026-08-24 12:48:06',2,'2026-08-24 12:48:06'),(22,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_12-53-17_685996.jpg',NULL,NULL,NULL,'2026-08-24 12:53:17',1,'2026-08-24 12:53:17'),(23,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_12-54-44_214618.jpg',1,'2026-08-24 16:48:23','','2026-08-24 12:54:44',1,'2026-08-24 12:54:44'),(24,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_13-00-24_399594.jpg',NULL,NULL,NULL,'2026-08-24 13:00:24',1,'2026-08-24 13:00:24'),(25,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_13-02-34_551630.jpg',NULL,NULL,NULL,'2026-08-24 13:02:34',1,'2026-08-24 13:02:34'),(26,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_13-03-13_521673.jpg',NULL,NULL,NULL,'2026-08-24 13:03:13',1,'2026-08-24 13:03:13'),(27,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_13-06-01_815829.jpg',NULL,NULL,NULL,'2026-08-24 13:06:01',1,'2026-08-24 13:06:01'),(28,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_13-08-29_331772.jpg',NULL,NULL,NULL,'2026-08-24 13:08:29',1,'2026-08-24 13:08:29'),(29,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_13-10-04_718229.jpg',NULL,NULL,NULL,'2026-08-24 13:10:04',1,'2026-08-24 13:10:04'),(30,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_13-16-05_868370.jpg',NULL,NULL,NULL,'2026-08-24 13:16:05',1,'2026-08-24 13:16:05'),(31,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_13-28-03_979384.jpg',NULL,NULL,NULL,'2026-08-24 13:28:03',1,'2026-08-24 13:28:03'),(32,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_16-44-17_841204.jpg',NULL,NULL,NULL,'2026-08-24 16:44:17',1,'2026-08-24 16:44:17'),(33,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_16-44-22_529455.jpg',NULL,NULL,NULL,'2026-08-24 16:44:22',1,'2026-08-24 16:44:22'),(34,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_16-44-27_966167.jpg',NULL,NULL,NULL,'2026-08-24 16:44:27',1,'2026-08-24 16:44:27'),(35,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_16-44-46_309633.jpg',1,'2026-08-24 16:50:26','','2026-08-24 16:44:46',1,'2026-08-24 16:44:46'),(36,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_16-44-55_533044.jpg',NULL,NULL,NULL,'2026-08-24 16:44:55',1,'2026-08-24 16:44:55'),(37,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_16-45-17_218142.jpg',NULL,NULL,NULL,'2026-08-24 16:45:17',1,'2026-08-24 16:45:17'),(38,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_16-45-51_534974.jpg',NULL,NULL,NULL,'2026-08-24 16:45:51',1,'2026-08-24 16:45:51'),(39,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_16-45-56_907823.jpg',1,'2026-08-24 16:51:45','','2026-08-24 16:45:56',1,'2026-08-24 16:45:56'),(40,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_16-46-09_156638.jpg',NULL,NULL,NULL,'2026-08-24 16:46:09',1,'2026-08-24 16:46:09'),(41,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_16-46-32_698239.jpg',NULL,NULL,NULL,'2026-08-24 16:46:32',1,'2026-08-24 16:46:32'),(42,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_16-47-11_314716.jpg',NULL,NULL,NULL,'2026-08-24 16:47:11',1,'2026-08-24 16:47:11'),(43,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_16-47-11_622671.jpg',NULL,NULL,NULL,'2026-08-24 16:47:11',1,'2026-08-24 16:47:11'),(44,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-24_16-47-11_878706.jpg',NULL,NULL,NULL,'2026-08-24 16:47:11',1,'2026-08-24 16:47:11'),(45,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-25_00-52-28_073903.jpg',NULL,NULL,NULL,'2026-08-25 00:52:28',1,'2026-08-25 00:52:28'),(46,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-27_17-39-48_729939.jpg',NULL,NULL,NULL,'2026-08-27 17:39:48',1,'2026-08-27 17:39:48'),(47,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-28_15-35-22_648950.jpg',1,'2026-08-28 15:43:03','','2026-08-28 15:35:22',1,'2026-08-28 15:35:22'),(48,'http://127.0.0.1:8080/pases/yolo1/record/img/result_2026-08-31_16-04-09_544598.jpg',NULL,NULL,NULL,'2026-08-31 16:04:09',1,'2026-08-31 16:04:09');
/*!40000 ALTER TABLE `detect_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detect_record_item`
--

DROP TABLE IF EXISTS `detect_record_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detect_record_item` (
  `item_id` int NOT NULL AUTO_INCREMENT COMMENT '明细主键',
  `record_id` int NOT NULL COMMENT '关联 detect_record.id',
  `disease_id` int DEFAULT NULL,
  `disease_name` varchar(100) NOT NULL COMMENT '冗余：YOLO识别病害名',
  `confidence` decimal(5,4) NOT NULL COMMENT '置信度',
  `item_audit_status` tinyint NOT NULL COMMENT '0-无需审核 1-待确认 2-已确认 3-误报 4-治理中 5-治',
  `final_disease_id` int DEFAULT NULL,
  `final_result` varchar(100) DEFAULT NULL COMMENT '冗余：人工确认病害名',
  `update_time` datetime DEFAULT NULL,
  `disease_type` int DEFAULT NULL,
  PRIMARY KEY (`item_id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='检测明细子表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detect_record_item`
--

LOCK TABLES `detect_record_item` WRITE;
/*!40000 ALTER TABLE `detect_record_item` DISABLE KEYS */;
INSERT INTO `detect_record_item` VALUES (1,3,1,'秋黏虫幼虫',0.9685,5,9,'黄茎螟幼虫','2026-08-31 17:47:30',1),(2,4,11,'灰斑病',0.7721,1,11,'灰斑病','2026-08-23 17:27:03',0),(3,4,11,'灰斑病',0.6541,1,11,'灰斑病','2026-08-23 17:27:03',0),(4,5,10,'枯萎病',0.7206,1,10,'枯萎病','2026-08-23 17:28:21',0),(5,9,10,'枯萎病',0.7206,1,10,'枯萎病','2026-08-23 17:51:53',0),(6,11,10,'枯萎病',0.7206,1,10,'枯萎病','2026-08-23 18:10:03',0),(7,18,8,'黄秆蛀虫',0.9397,1,8,'黄秆蛀虫','2026-08-23 18:27:49',1),(8,18,10,'枯萎病',0.5282,1,10,'枯萎病','2026-08-23 18:27:49',0),(9,18,9,'黄秆蛀虫幼虫',0.5125,1,9,'黄秆蛀虫幼虫','2026-08-23 18:27:49',1),(10,21,10,'枯萎病',0.9263,1,10,'枯萎病','2026-08-24 12:48:06',0),(11,23,4,'玉米肿瘤病',0.7915,1,4,'玉米肿瘤病','2026-08-24 12:54:44',0),(12,23,4,'玉米肿瘤病',0.7212,1,4,'玉米肿瘤病','2026-08-24 12:54:44',0),(13,23,4,'玉米肿瘤病',0.6950,2,4,'玉米肿瘤病','2026-08-24 16:48:23',0),(14,23,4,'玉米肿瘤病',0.4496,1,4,'玉米肿瘤病','2026-08-24 12:54:44',0),(15,26,1,'秋黏虫幼虫',0.9577,1,1,'秋黏虫幼虫','2026-08-24 13:03:13',1),(16,35,10,'枯萎病',0.9263,2,10,'枯萎病','2026-08-24 16:50:26',0),(17,39,10,'枯萎病',0.9263,3,10,'枯萎病','2026-08-24 16:51:45',0),(18,45,10,'枯萎病',0.9263,1,10,'枯萎病','2026-08-25 00:52:28',0),(19,46,10,'枯萎病',0.8251,1,10,'枯萎病','2026-08-27 17:39:48',0),(20,47,10,'枯萎病',0.8251,2,10,'枯萎病','2026-08-28 15:43:03',0),(21,48,10,'枯萎病',0.8251,2,10,'枯萎病','2026-08-31 16:04:09',0);
/*!40000 ALTER TABLE `detect_record_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `disease_knowledge`
--

DROP TABLE IF EXISTS `disease_knowledge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `disease_knowledge` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '病害ID',
  `disease_name` varchar(100) NOT NULL COMMENT '病虫害名称（与YOLO类别严格一致）',
  `symptom` text COMMENT '典型症状',
  `treatment` text COMMENT '治理处理方案',
  `create_time` datetime DEFAULT NULL COMMENT '录入时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `disease_type` tinyint NOT NULL COMMENT '0-病害 1-虫害',
  `example_url` varchar(255) NOT NULL COMMENT '样例实物图片',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='病害知识库';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `disease_knowledge`
--

LOCK TABLES `disease_knowledge` WRITE;
/*!40000 ALTER TABLE `disease_knowledge` DISABLE KEYS */;
INSERT INTO `disease_knowledge` VALUES (4,'玉米肿瘤病','玉米果穗或者茎秆长出肿大畸形的瘤状病包，初期表面发白，后期内部充满黑色黑粉孢子，病瘤会膨大扭曲，破坏玉米果穗，造成颗粒畸形损毁。','1. 农业防治：选用抗病品种；轮作倒茬，不要连年重茬种玉米；在病瘤变黑破裂之前，把病瘤摘除带出田外销毁，避免孢子扩散。\r\n2. 种子处理：播种前对种子进行药剂拌种，杀灭种子携带病菌。\r\n3. 田间管理：避免偏施氮肥；农事操作减少植株伤口，病菌主要从伤口侵入。\r\n4. 化学防治：发病初期喷施三唑类杀菌剂，减少孢子传播侵染。','2026-08-23 17:04:30',NULL,0,'/pases/upload-demo/static/knowledge/20260823_145839586950_2cccc_jpg.rf.4adca21fea76f0c0564d748fbaa23923.jpg'),(6,'褐斑病','初期：叶片、叶鞘交接位置出现圆形、椭圆形黄色水渍状褪绿小点，斑点很小，分散或成串排布，叶片局部轻微发黄，肉眼不易分辨。\r\n中期：病斑隆起鼓起，手感粗糙，转为红褐色、紫褐色疱状斑点；病斑沿着叶脉成串成片聚集，叶鞘、茎节部位病斑更大，多个小病斑互相连接成大斑块。\r\n后期：病斑表皮破裂，释放褐色粉末孢子；受害叶片发黄枯死，叶鞘腐烂，叶片可从病斑处折断；严重时整株叶片干枯，植株长势衰退。\r\n危害部位：叶片、叶鞘、茎节，叶鞘‑叶片交界处发病最重。','农业防治：选用抗病玉米品种；轮作倒茬；收获后把病秸秆清出田外销毁，减少土壤病菌。\r\n物理 / 生物防治：种子筛选，剔除带病籽粒；增施磷钾肥，减少氮肥，提升植株抗病力。\r\n化学防治：发病初期喷施戊唑醇、苯醚甲环唑，7‑10 天一次，连续 2 次，叶片正反面、叶鞘位置均匀打药。\r\n田间管理：合理密植；雨后及时排水，降低田间湿度。','2026-08-23 17:04:30',NULL,0,'/pases/upload-demo/static/knowledge/20260823_152957564901_cffbb31e0be54ac49b006cedea6e9188tplv-a9rns2rl98-pc_smart_face_crop-v1_512_384.webp'),(7,'霜霉病','初期：幼苗和成株叶片出现淡黄绿色、浅黄白色的褪绿条纹、斑块，沿着叶脉方向扩展，叶片局部失绿，无明显坏死孔洞，植株长势变慢。\r\n中期：叶片褪绿斑纹不断扩大，黄绿相间长条大斑；湿度大时叶片背面长出灰白色、淡紫灰色霜状霉层，这是病菌孢子层；叶片逐步发黄。\r\n后期：病斑变为黄褐色，叶片大面积干枯坏死；严重病株矮化畸形，不能正常抽穗结实；湿度大时霉层非常明显，干燥时霉层会消退。','农业防治：选用抗病玉米品种；实行轮作；拔除早期病株带出田外销毁，减少病菌扩散；收获后清理病残秸秆。\r\n物理 / 生物防治：播种前筛选种子，剔除病粒；种子药剂浸种拌种；合理施肥，增施磷钾肥提高植株抗性。\r\n化学防治：发病初期喷施甲霜灵、烯酰吗啉，间隔 7‑10 天喷施一次，连续 2‑3 次，叶片背面重点喷施。\r\n田间管理：合理密植；雨后及时排水，降低田间土壤和空气湿度；避免大水漫灌。','2026-08-23 17:04:30',NULL,0,'/pases/upload-demo/static/knowledge/20260823_153218629915_OIP-C.webp'),(8,'黄茎螟蛀虫','初期：低龄幼虫体型细小，淡黄褐色，藏在玉米心叶内部取食；心叶展开后叶片出现一排排规则的小圆虫孔，叶片出现花叶；茎秆外表可见细小蛀入小孔，外部不易发现虫体。\r\n中期：幼虫体长变大，体色黄白至灰褐色，身体背侧有褐色纵向条纹；幼虫钻入茎秆内部蛀食髓部，茎秆外部可见蛀孔，蛀孔处排出黄褐色虫粪碎屑；受害植株心叶萎蔫，雄穗容易折断；部分幼虫顺着花丝钻入果穗啃食籽粒。\r\n后期：老熟幼虫在茎秆、果穗内部蛀成粗大虫道，茎秆内部中空；受害茎秆发黄干枯，极易遇风倒伏折断；果穗籽粒被蛀破损，虫粪残留穗内，容易诱发穗腐霉变；老熟幼虫在秸秆内越冬。','农业防治：选用抗螟玉米品种；收获之后彻底处理玉米秸秆，粉碎或烧毁，消灭秸秆内越冬幼虫；与大豆、花生等非禾本科作物轮作。\r\n物理 / 生物防治：田间布设杀虫灯诱杀成虫；释放赤眼蜂寄生虫卵；心叶期施用白僵菌、Bt 颗粒剂。\r\n化学防治：大喇叭口期为关键防治期，把药剂撒入心叶；药剂选用氯虫苯甲酰胺、甲维盐；穗期重点喷施果穗花丝部位。\r\n田间管理：及时清除田边杂草；合理水肥，避免植株徒长；倒伏植株及时清理出田外。','2026-08-23 17:04:30',NULL,1,'/pases/upload-demo/static/knowledge/20260823_154000192362_f472e22a33e04cd78550d9a379f4a2b5.jpeg'),(9,'黄茎螟幼虫','初期（1‑2 龄低龄幼虫）：体长 1.5‑5mm，头部黑褐色，虫体乳白色半透明，体型细小；多群集躲藏在玉米心叶内部啃食叶肉，只留下叶片表皮，叶片出现半透明筛网状花叶；可吐丝下垂随风扩散转移植株；外表很难直接看见虫体，只能看到叶片受害花叶症状。\r\n中期（3‑4 龄幼虫）：体长 8‑18mm，头部棕黑，虫体变为浅黄褐色、淡红褐色；身体圆筒形，体节分明，中后胸、腹部每节分布圆形黑色毛瘤，背部可见 3 条褐色纵向纹路；3 龄后食量增大，心叶展开后出现标志性**整齐横向排孔**；4 龄开始钻蛀，钻入茎秆、雄穗柄，蛀孔外部堆积黄褐色颗粒虫粪；也会爬到果穗花丝处啃食花丝陕西省农业...。\r\n后期（老熟 5 龄幼虫）：体长 20‑30mm，头部深褐色，体色灰褐色至淡红褐色；体节毛瘤清晰凸起，背部纵纹明显；主要藏匿在茎秆、穗轴虫道内部；蛀食茎秆髓部，造成茎秆中空；钻蛀果穗啃食籽粒，虫粪残留在果穗缝隙；老熟幼虫直接在秸秆虫道内越冬。','农业防治：选用抗螟玉米品种；收获后秸秆粉碎还田或带出田外销毁，杀死越冬老熟幼虫；和大豆、花生轮作，降低虫源。\r\n物理 / 生物防治：田间安装杀虫灯诱杀成虫；产卵期释放赤眼蜂；大喇叭口期施用 Bt、白僵菌颗粒剂；人工摘除受害心叶。\r\n化学防治：大喇叭口期是关键防治窗口，药剂撒入心叶；药剂选用氯虫苯甲酰胺、甲维盐；穗期重点喷施花丝部位。\r\n田间管理：清除田边杂草，减少成虫产卵栖息；均衡施肥，避免植株徒长；及时清理折断受害植株。','2026-08-23 17:04:30',NULL,1,'/pases/upload-demo/static/knowledge/20260823_162020576087_0097875116088950100_0302_0002.jpg'),(10,'枯萎病','初期：根系首先受害，部分须根、侧根变为黄褐色，根系活力下降；地上植株外观基本正常，中午高温强光条件下中下部叶片短暂萎蔫下垂，傍晚、清晨可以恢复原状，茎秆外表看不到明显病斑，不容易发现病害。\r\n中期：根系大量腐烂变黑，根皮容易脱落，次生根数量大幅减少；茎秆基部 1‑3 节间内部维管束变褐，茎秆外部出现淡褐色水渍状斑块；植株下部叶片由下向上褪绿发黄，部分植株呈现青枯状态，叶片保持灰绿色但萎蔫下垂；不再恢复，果穗开始发育不良，果穗柄变软。湿度大时茎节处可见淡粉红色霉层（镰刀菌孢子）。\r\n后期：根系完全腐烂坏死，植株极易直接拔起；茎秆基部节间变软腐烂，内部髓组织解体松散，只剩丝状纤维；整株叶片全部枯黄干枯，整株枯死；果穗倒挂下垂，籽粒干瘪皱缩，产量严重损失；大风天气极易倒伏绝收。','农业防治：选用抗病玉米杂交品种；实行 2‑3 年轮作，和大豆、花生等非禾本科作物轮作；收获之后彻底清理田间病残秸秆，减少土壤病菌来源。\r\n物理 / 生物防治：播种前种子药剂拌种；增施磷钾肥，减少氮肥，提高植株抗逆；使用木霉菌等生物菌剂处理种子或土壤。\r\n化学防治：发病初期，喷施恶霉灵、氰烯菌酯，重点喷淋根茎基部；病害早期灌根处理，抑制根系侵染。\r\n田间管理：合理密植；雨后及时排水，杜绝田间积水；农事操作避免损伤玉米根系；发现早期病株及时拔除带出田外销毁。','2026-08-23 17:04:30',NULL,0,'/pases/upload-demo/static/knowledge/20260823_162003895326_t015e78508d74f25029.jpg'),(11,'灰斑病','叶片上出现长条形、灰褐色至浅褐色的平行长条病斑，病斑顺着叶脉方向延伸，病斑颜色灰白灰褐色，严重时病斑连片，整张叶片枯死，高温高湿环境容易爆发。','1. 农业防治：收获之后清除田间病残秸秆；轮作，避免连年种植玉米；选用抗病玉米品种。\r\n2. 田间管理：合理密植，不要种植过密；平衡施肥，增施磷钾肥，提高植株抗病能力。\r\n3. 化学防治：发病初期喷施苯醚甲环唑、戊唑醇等杀菌剂，间隔 7‑10 天补喷一次。','2026-08-23 17:04:30',NULL,0,'/pases/upload-demo/static/knowledge/20260823_162536665990_0a01cc10-3892-4311-9c48-0ac6ab3c7c43___RS_GLSp-9352_270deg_JPG_jpg.rf.0ec4c08f9a7408d0a06995f6fa28bd4c.jpg');
/*!40000 ALTER TABLE `disease_knowledge` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT COMMENT '用户唯一ID',
  `username` varchar(50) NOT NULL COMMENT '登录账号',
  `password` varchar(255) NOT NULL COMMENT '加密密码',
  `phone` varchar(20) DEFAULT NULL COMMENT '手机号',
  `role` varchar(20) NOT NULL COMMENT '1=admin管理员，0=普通用户',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','123',NULL,'1',NULL),(2,'zhangsan','1234','','0','2026-08-23 16:49:24'),(3,'lisi','123','','0','2026-08-23 17:00:10'),(4,'wangwu','123','','0','2026-08-23 17:04:00'),(7,'string','string','string','string','2026-08-31 17:36:26'),(8,'string','string','string','string','2026-08-31 17:37:26');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'pases'
--
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-02 13:39:35
