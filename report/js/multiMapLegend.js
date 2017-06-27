var mapLegendSvg = d3.select(".multsLegend")
  .append("svg")
    .attr("width",120)
    .attr("height",110);

mapLegendSvg.append("text")
  .attr("x",2)
  .attr("y",20)
  .attr("fill","#444")
  .style("font-family","Gentium Book Basic")
  .text("Legend");

mapLegendSvg.append("line")
  .attr('x1',2)
  .attr('y1',40)
  .attr('x2',30)
  .attr('y2',40)
  .attr("stroke-width",3)
  .attr("stroke-linecap","round")
  .attr("stroke","#4f8b2d");
mapLegendSvg.append("text")
  .attr("x",40)
  .attr("y",42)
  .attr("fill","#444")
  .style("font-size","10px")
  .text("Both Directions");

mapLegendSvg.append("line")
  .attr('x1',2)
  .attr('y1',60)
  .attr('x2',30)
  .attr('y2',60)
  .attr("stroke-width",3)
  .attr("stroke-linecap","round")
  .attr("stroke","#95cc75");
mapLegendSvg.append("text")
  .attr("x",40)
  .attr("y",62)
  .attr("fill","#444")
  .style("font-size","10px")
  .text("One Direction");

mapLegendSvg.append("line")
  .attr('x1',2)
  .attr('y1',80)
  .attr('x2',30)
  .attr('y2',80)
  .attr("stroke-width",3)
  .attr("stroke-linecap","round")
  .attr("stroke","#ddd");
mapLegendSvg.append("text")
  .attr("x",40)
  .attr("y",82)
  .attr("fill","#444")
  .style("font-size","10px")
  .text("Neither Direction");
