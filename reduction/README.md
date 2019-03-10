Running the reduction code
===
folder_name specifies the folder in which the forward and backward files are present. All the forward
files should be of the form forward-edge-* and all the backward files should be of the form backward-edge-*
The resultant csvs get saved in reduction/.

The following needs to be done one time. 

```shell
pip install -r requirements.txt
```

```shell
cd reduction
python reduction.py <folder_name>
```

Visualizing reduced graph:
```shell
sudo service neo4j stop
sudo rm -rf /var/lib/neo4j/data/databases/graph.db
sudo service neo4j start
cd parser/
$ sudo ./neo4j-load-reduced-csv.sh .
```
The above command will access the reduced csvs in the reduction/ directory and generate graphs in neo4j database. 


Performance Improvement
===
Early versions of our code were taking hours to reduce logs worth just minutes. We were able to drastically improve our runtime by exploiting the fact that logs are sorted chronologically.

In order to check forward and backward dependencies we need to access the parents and children for different nodes (If a directed edge goes from u to v, u is the parent and v is the child).  The information of these parents and children are saved in the form of two adjacency lists. We populate these lists initially at the beginning of the algorithm. For every parent, its children (and their corresponded edges) and for every child, its parents (and their corresponded edges) are saved in the chronological order in these lists.

According to the algorithm, after checking the dependencies, if there is a reduction i.e. two edges need to be replaced by 1, we eliminate the edge from the lists mentioned above. Since each edge has a unique id, we know the id that needs to be deleted (the edge that is redundant according to the reduction algorithm). Here, we use binary search to search the redundant edge id in the lists mentioned above, as opposed to using a linear search being used initially.

This decreased the complexity from O(n) to O(logn) and drastically reduced the reduction time for large logs (for eg. 36 hour logs).
