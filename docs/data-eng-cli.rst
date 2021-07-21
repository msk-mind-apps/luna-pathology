Data Engineering CLIs
=====================

Luna Pathology offers data ingestion and data processing CLIs.

The data ingestion CLIs organize your pathology images and annotations with appropriate metadata. The data processing CLIs convert the pathology annotations into various formats compatible
with other open-source tools like Qupath.

Note that the data ingestion CLIs rely on APIs that retrieve annotations from internal data sources.

Whole Slide Image (WSI) CLI
---------------------------
This module captures the metadata of your slides in a table.

.. click:: luna_pathology.proxy_table.generate:cli
   :prog: luna_pathology.proxy_table.generate

Annotation CLIs
---------------
This module downloads point-click nuclear annotations and regional annotations, then converts them to geojson format.

.. click:: luna_pathology.point_annotation.proxy_table.generate:cli
   :prog: luna_pathology.point_annotation.proxy_table.generate
   :nested: full

.. click:: luna_pathology.point_annotation.refined_table.generate:cli
   :prog: luna_pathology.point_annotation.refined_table.generate
   :nested: full

.. click:: luna_pathology.refined_table.regional_annotation.dask_generate:cli
   :prog: luna_pathology.refined_table.regional_annotation.dask_generate
   :nested: full
