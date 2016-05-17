-- Changes: Added exo planets columns to `star` table. Added schema for `planet` table

USE `astronomy`;

ALTER TABLE `star` ADD `teff` FLOAT UNSIGNED NULL AFTER `uvw`, ADD `logg` FLOAT UNSIGNED NULL AFTER `teff`, ADD `mass` FLOAT UNSIGNED NULL COMMENT 'M_S' AFTER `logg`, ADD `vsini` FLOAT UNSIGNED NULL COMMENT 'km/s' AFTER `mass`, ADD `multiple_planets` TINYINT UNSIGNED NULL DEFAULT NULL COMMENT '(0=N, 1=Y, 2=NA)' AFTER `vsini`;

-- phpMyAdmin SQL Dump
-- version 4.4.10
-- http://www.phpmyadmin.net
--
-- Host: localhost:3306
-- Generation Time: May 17, 2016 at 11:06 AM
-- Server version: 5.5.42
-- PHP Version: 5.6.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Database: `astronomy`
--

-- --------------------------------------------------------

--
-- Table structure for table `planet`
--

CREATE TABLE `planet` (
  `name` char(4) NOT NULL,
  `hip` char(12) CHARACTER SET ascii NOT NULL,
  `m_p` char(32) DEFAULT NULL COMMENT 'M_J',
  `p` char(32) DEFAULT NULL COMMENT 'd',
  `e` char(32) DEFAULT NULL,
  `a` char(32) DEFAULT NULL COMMENT 'AU',
  `created_at` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `planet`
--
ALTER TABLE `planet`
  ADD PRIMARY KEY (`name`,`hip`) USING BTREE,
  ADD KEY `planet_star_fk` (`hip`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `planet`
--
ALTER TABLE `planet`
  ADD CONSTRAINT `planet_star_fk` FOREIGN KEY (`hip`) REFERENCES `star` (`hip`) ON DELETE CASCADE ON UPDATE CASCADE;
