-- phpMyAdmin SQL Dump
-- version 4.4.10
-- http://www.phpmyadmin.net
--
-- Host: localhost:3306
-- Generation Time: Mar 24, 2016 at 10:00 AM
-- Server version: 5.5.42
-- PHP Version: 5.6.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Database: `astronomy`
--
CREATE DATABASE IF NOT EXISTS `astronomy` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
USE `astronomy`;

-- --------------------------------------------------------

--
-- Table structure for table `catalogue`
--
-- Creation: Mar 24, 2016 at 08:09 AM
--

DROP TABLE IF EXISTS `catalogue`;
CREATE TABLE `catalogue` (
  `id` tinyint(3) unsigned NOT NULL,
  `author_year` char(64) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `composition`
--
-- Creation: Mar 17, 2016 at 08:03 AM
--

DROP TABLE IF EXISTS `composition`;
CREATE TABLE `composition` (
  `hip` char(12) CHARACTER SET ascii NOT NULL,
  `cid` tinyint(3) unsigned NOT NULL,
  `element` char(8) NOT NULL,
  `value` float NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Composition elements of each star';

-- --------------------------------------------------------

--
-- Table structure for table `star`
--
-- Creation: Mar 18, 2016 at 04:06 AM
--

DROP TABLE IF EXISTS `star`;
CREATE TABLE `star` (
  `hip` char(12) CHARACTER SET ascii NOT NULL,
  `hd` char(12) CHARACTER SET ascii DEFAULT NULL,
  `bd` char(16) CHARACTER SET ascii COLLATE ascii_bin DEFAULT NULL,
  `hr` char(12) CHARACTER SET ascii DEFAULT NULL,
  `spec` char(8) CHARACTER SET ascii COLLATE ascii_bin DEFAULT NULL,
  `vmag` char(12) CHARACTER SET ascii DEFAULT NULL,
  `bv` char(8) CHARACTER SET ascii DEFAULT NULL,
  `dist` tinyint(11) unsigned DEFAULT NULL COMMENT 'distance from our sun. Stars in Hypatia are ONLY included if they are < 150 pc away.',
  `rascension` float DEFAULT NULL COMMENT '-360 to 360, longitude',
  `declination` float DEFAULT NULL COMMENT '-90 to 90, latitude',
  `position` char(32) CHARACTER SET armscii8 DEFAULT NULL COMMENT 'Position converts the polar coordinates, namely RA, Dec, and dist, to rectangular coordinates, where the Sun is at the center',
  `disk` enum('thin','thick','halo','') CHARACTER SET ascii COLLATE ascii_bin DEFAULT NULL,
  `uvw` char(32) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `catalogue`
--
ALTER TABLE `catalogue`
  ADD PRIMARY KEY (`id`) USING HASH,
  ADD UNIQUE KEY `author_year` (`author_year`);

--
-- Indexes for table `composition`
--
ALTER TABLE `composition`
  ADD PRIMARY KEY (`hip`,`cid`,`element`),
  ADD KEY `hip_fk_index` (`hip`) USING BTREE,
  ADD KEY `catalogue_id_fk_index` (`cid`) USING HASH;

--
-- Indexes for table `star`
--
ALTER TABLE `star`
  ADD PRIMARY KEY (`hip`) USING HASH;

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `catalogue`
--
ALTER TABLE `catalogue`
  MODIFY `id` tinyint(3) unsigned NOT NULL AUTO_INCREMENT;
--
-- Constraints for dumped tables
--

--
-- Constraints for table `composition`
--
ALTER TABLE `composition`
  ADD CONSTRAINT `composition_catalogue_fk` FOREIGN KEY (`cid`) REFERENCES `catalogue` (`id`) ON UPDATE CASCADE,
  ADD CONSTRAINT `composition_star_fk` FOREIGN KEY (`hip`) REFERENCES `star` (`hip`) ON DELETE CASCADE ON UPDATE CASCADE;

