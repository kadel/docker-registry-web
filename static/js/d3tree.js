
// based on http://bl.ocks.org/d3noob/8329404 

// *********** Convert flat data into a nice tree ***************
// create a name: node map
var dataMap = data.reduce(function(map, node) {
	map[node.name] = node;
	return map;
}, {});

// create the tree array
var treeData = [];
data.forEach(function(node) {
	// add to parent
	var parent = dataMap[node.parent];
	if (parent) {
		// create child array if it doesn't exist
		(parent.children || (parent.children = []))
			// add node to child array
			.push(node);
	} else {
		// parent is null or missing
		treeData.push(node);
	}
});

// ************** Generate the tree diagram	 *****************
var margin = {top: 20, right: 10, bottom: 10, left: 20},
	width = 600 - margin.right - margin.left,
	height = 600 - margin.top - margin.bottom;
	
var i = 0;

var tree = d3.layout.tree()
	.size([width, height]);

var diagonal = d3.svg.diagonal()
	.projection(function(d) { return [d.x, d.y]; });

  function zoomed() {
    d3.event.sourceEvent.stopPropagation();
    svg.attr("transform", "translate("
        + (d3.event.translate[0] + margin.left) + ","
        + (d3.event.translate[1] + margin.top) + ")scale(" + d3.event.scale + ")");
  }

  var zoomListener = d3.behavior.zoom()
    .scaleExtent([0.3, 3])
    .on("zoom", zoomed);


var svg = d3.select("#graph").append("svg")
    .call(zoomListener)
    .attr("class", "graph")
	.attr("width", width + margin.right + margin.left)
	.attr("height", height + margin.top + margin.bottom)
  .append("g")
	.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

root = treeData[0];

update(root);

function update(source) {

  // Compute the new tree layout.
  var nodes = tree.nodes(root).reverse(),
	  links = tree.links(nodes);

  // Normalize for fixed-depth.
  nodes.forEach(function(d) { d.y = d.depth * 60; });

  // Declare the nodes…
  var node = svg.selectAll("g.node")
	  .data(nodes, function(d) { return d.id || (d.id = ++i); });

  // Enter the nodes.
  var nodeEnter = node.enter().append("g")
	  .attr("class", "node")
	  .attr("transform", function(d) {
		  return "translate(" + d.x + "," + d.y + ")"; });

  var onclickFce = function(d) {return window.location=d.imageid};

  nodeEnter.append("circle")
	  .attr("r", 10)
	  .style("fill", "#fff")
	  .on("click", onclickFce)
	  ;;;

  nodeEnter.append("text")
	  .attr("x", function(d) { 
		  return d.children  })//|| d._children ? -13 : 13; })
	  .attr("dy", "22px")
	  .attr("text-anchor", function(d) { 
		  return "middle" })//|| d._children ? "end" : "start"; })
	  .text(function(d) {
		   label = d.name
		   if (d.maintagname != null) label = d.maintagname;
		   if (d.author != null) label += " (" + d.author + ") ";
		   return label; })  //+ d.created;
	  .style("fill-opacity", 1)
	  .on("click", onclickFce)
	  ;;

  // Declare the links…
  var link = svg.selectAll("path.link")
	  .data(links, function(d) { return d.target.id; });

  // Enter the links.
  link.enter().insert("path", "g")
	  .attr("class", "link")
	  .attr("d", diagonal);

}


