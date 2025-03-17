=============
Release Notes
=============

Version history
--------------------

+------------+----------+----------------------------------------+----------------------+
|  **Date**  | **Ver.** |               **Author**               |      **Comment**     | 
+============+==========+========================================+======================+
| 2025-03-17 |   1.1.0  | `@bbglab <https://github.com/bbglab>`_ | Patch release        |
|            |          |                                        |                      |
+------------+----------+----------------------------------------+----------------------+
| 2024-12-12 |   1.0.1  | `@bbglab <https://github.com/bbglab>`_ | Patch release        |
|            |          |                                        |                      |
+------------+----------+----------------------------------------+----------------------+
| 2024-07-25 |   1.0.0  | `@bbglab <https://github.com/bbglab>`_ | First stable release | 
|            |          |                                        |                      | 
+------------+----------+----------------------------------------+----------------------+

OpenVariant v1.1.0
==================

This version includes the following features:

* Fixed Python (**3.12 - 3.13**) incompatibilities on plugin creation command.
* Replaced `error` for `warning` on empty line cases.
* Be able to skip unreadable files and directories (added `--skip` flag on commands)

OpenVariant v1.0.1
==================

This version includes the following features:

* Fixed Python (**3.12 - 3.13**) incompatibilities.
* Fixed some security vulnerabilities on outdated packages.

OpenVariant v1.0.0
==================

First stable release of OpenVariant. This version includes the following features:

* Tasks: **find** files, **cat** operation and **group-by**.
* Plugin system: classification of **alteration type**, **alternate allele frequency** getter and **LiftOver** operation.