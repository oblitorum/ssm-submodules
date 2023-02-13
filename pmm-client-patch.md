- Backport of compatibility patch for kernels 4.19+ which changed the format of /proc/diskstats.
    Modified version of the upstream patch backported for the older node_exporter base:
    https://github.com/prometheus/node_exporter/pull/1109
- Update percona-toolkit to 3.4.0
- fix innodb_metrics for mariadb 10.5+

    * determine column name for innodb_metrics before
    querying
    adds support more mariadb 10.5+
- Fix pmm-admin check-network ssl check not compatible with Go >= 1.12
- Fix bug that caused each upgrade to add an extra textfile listener. This caused a huge volume of spurious errors to get logged.
