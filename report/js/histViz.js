
var histsvg = d3.select("#histVizSvg"),
    histmargin = {top: 10, right: 2, bottom: 40, left: 20},
    histwidth = Number(d3.select("#histVizSvg").style("width").split("px")[0]) - histmargin.left - histmargin.right,
    histheight = 400 - histmargin.top - histmargin.bottom;


var histMode = 'bar';
var legroom = 20;
var simCircRad = 3;
var formatValue = d3.format(".2%");

var yH = d3.scaleLinear()
    .domain([0, 1.0])
    .range([histheight, 0]);
var yB = d3.scaleLinear()
    .domain([0, 0.5])
    .range([histheight, 0]);

var histx = d3.scaleLinear()
    .range([0, histwidth]);

var histcolor = d3.scaleOrdinal()
      .range(["#69b93c","#58BFAC","#4682B4","#53575A","#914D90","#ED7664","#FFC445"]);

var histg = histsvg.append("g")
    .attr("transform", "translate(" + histmargin.left + "," + histmargin.top + ")");

d3.csv("./data/modelResultsOverview.csv", type, function(error, data) {
  if (error) throw error;

  //y.domain(d3.extent(data, function(d) { return d.value; }));
  histx = d3.scaleBand()
    .domain(data.map(function(d) { return d.method; }))
    .rangeRound([histmargin.left, histwidth - histmargin.right])
    .padding(0.33);
  histcolor.domain(data.map(function(d) { return d.method; }));
  //y.domain(d3.extent(data, function(d) { return d.value; }));

  var simulationh = d3.forceSimulation(data)
      .force("x", d3.forceX(function(d) { return histx(d.method)+histx.bandwidth()/2;}))
      .force("y", d3.forceY(function(d) { return yH(d.value); }).strength(1))
      .force("collide", d3.forceCollide(4))
      .stop();

  for (var i = 0; i < 120; ++i) simulationh.tick();

  histg.append("g")
      .attr("class", "axis axis--y")
      .attr("transform", "translate(" + (-histmargin.left) + ",0)")
      .call(d3.axisRight(yB).ticks(10, ".0%"));

  histg.append("g")
    .attr("class", "axis axis--x")
    .attr("transform", "translate(0," + (0+yB(0)) + ")")
    .call(d3.axisBottom(histx));

  var histcell = histg.append("g")
      .attr("class", "histcells")
    .selectAll(".cellg").data(d3.voronoi()
        .extent([[-histmargin.left, -histmargin.top], [histwidth + histmargin.right, histheight + histmargin.top]])
        .x(function(d) { return d.x; })
        .y(function(d) { return d.y; })
      .polygons(data)).enter().append("g").attr("class","cellg");

  histcell.append("circle")
      .attr("r", 0)
      .attr("class","simCirc")
      .attr("fill", function(d){return (histcolor(d.data.method));})
      .attr("stroke", function(d){return (histcolor(d.data.method));})
      .attr("name", function(d) { return d.data.name.replace(/[- )(]/g,''); })
      .attr("dir", function(d) { return d.data.dir; })
      .attr("cx", function(d) { return d.data.x; })
      .attr("cy", function(d) { return d.data.y; });

  histcell.append("path")
      .attr("d", function(d) { return "M" + d.join("L") + "Z"; });

  histcell.append("title")
      .text(function(d) { return (formatValue(d.data.value)+"\n"+d.data.name+"\n"+d.data.dir); });

  histcell.on("mouseout",function(d){
    if (histMode=='hist'){
      d3.selectAll(".simCirc").attr("opacity",1.0);
    }
  });
  histcell.on("mouseover",function(d){
    if (histMode=='hist'){
      d3.selectAll(".simCirc").attr("opacity",0.33);
      d3.selectAll(".simCirc[name="+ d.data.name.replace(/[- )(]/g,'') +"][dir="+d.data.dir+"]").attr("opacity",1);
    }
  });


  d3.json("./data/modelResultsOverview.json", function(error, jsondata) {
    var simbars = histg.selectAll(".simBar")
      .data(jsondata)
      .enter()
      .append("rect")
        .attr("class","simBar")
        .attr("fill", function(d){return (histcolor(d.method));})
        .attr("stroke", "none")
        .attr("x", function(d) { return histx(d.method);})
        .attr("y", function(d) { return yB(d.mean);})
        .attr("width", function(d) { return histx.bandwidth();})
        .attr("height",function(d) { return yB(0.5-d.mean);});
    simbars.append("title")
        .text(function(d) { return (formatValue(d.mean)); });
  });

});

function type(d) {
  if (!d.value) return;
  d.value = +d.value;
  return d;
}


d3.select("#histButton").on("click",function(){
  var histTrans = d3.transition()
    .duration(1500)
    .ease(d3.easeBounceOut);
  if (histMode=='bar'){
    histMode = 'hist';
    d3.select(this).html("hide details");
    //y.domain([0,1]);
    d3.select(".axis--y")
      .transition(histTrans)
      .call(d3.axisRight(yH).ticks(10, ".0%"));
    d3.selectAll(".simCirc")
      .transition(histTrans)
      .attr("r",simCircRad);
    d3.selectAll(".simBar")
      .transition(histTrans)
      .attr("opacity",1)
      .attr("y", function(d) { return yH(0)+legroom;})
      .attr("height",0);
    d3.select(".axis--x")
      .transition(histTrans)
      .attr("transform", "translate(0," + (legroom+yH(0)) + ")");
  }else{
    histMode = 'bar';
    d3.select(this).html("show details");
    //y.domain([0,0.5]);
    d3.select(".axis--y")
      .transition(histTrans)
      .call(d3.axisRight(yB).ticks(10, ".0%"));
    d3.selectAll(".simCirc")
      .transition(histTrans)
      .attr("r",0);
    d3.selectAll(".simBar")
      .transition(histTrans)
      .attr("opacity",1)
      .attr("y", function(d) { return yB(d.mean);})
      .attr("height",function(d) { return yB(0.5-d.mean);});
    d3.select(".axis--x")
      .transition(histTrans)
      .attr("transform", "translate(0," + (0+yB(0)) + ")");
  }

});
