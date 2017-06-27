// Dropdown Stuff
$(document).ready(function() {
  d3.json("./data/interstateList.json", function(error, io) {
    if (error) throw error;
    $(".singleHighwayDropDown").select2({
      data: io
    });
    $('.singleHighwayDropDown').select2().val(209).trigger("change");
  });
});

// Actual Map Stuff
var SINGLEHIGHWAY = {'width': 0, 'height':0}
SINGLEHIGHWAY.width  = Number(d3.select("#singleHighwayMap").style("width").split("px")[0]);
SINGLEHIGHWAY.height = Number(d3.select("#singleHighwayMap").style("height").split("px")[0]);
SINGLEHIGHWAY.marginY = 50;
SINGLEHIGHWAY.marginX = 20;
var shX = d3.scaleLinear()
            .domain([0,1150]) //comes out of python this way
            .range([SINGLEHIGHWAY.marginX, SINGLEHIGHWAY.width-SINGLEHIGHWAY.marginX]);
var shY = d3.scaleLinear()
            .domain([0,50]) //comes out of python this way
            .range([SINGLEHIGHWAY.marginY, SINGLEHIGHWAY.height-SINGLEHIGHWAY.marginY]);
var shprojection = d3.geoTransform({
  point: function(px, py) {
    this.stream.point(shX(px), shY(py));
  }
});


// Draw the Compass
var SHsvg = d3.select("#singleHighwayMap").append("svg")
    .attr("width", SINGLEHIGHWAY.width)
    .attr("height", SINGLEHIGHWAY.height);
var shpath = d3.path();
var voronoi = d3.voronoi()
    .extent([[0, 0], [SINGLEHIGHWAY.width, SINGLEHIGHWAY.height]]);
var shcell = SHsvg.append("g")
    .attr("class", "shvoronoi");
var compassG = SHsvg.append("g")
    .attr("id","compassG")
    .attr("width",24)
    .attr("height",30);
var compassLeft = compassG.append("path")
    .attr("id","compassL")
    .attr("d","M2,28 L12,2 L12,22 L2,28");
var compassRight = compassG.append("path")
    .attr("id","compassR")
    .attr("d","M22,28 L12,2 L12,22 L22,28");
var shcityText;


// Initialize the Viz

d3.json("./data/interstates/209.json", function(error, singleH) {
  if (error) throw error;

  // rotate that sweet sweet compass
  var isNS = 0;
  if (singleH.direction=="East"){
    isNS = 0;
    d3.select("#compassG")
      .transition()
      .duration(200)
      .attr("transform","translate(0,0) rotate(0)");

  }else{
    isNS = 1;
    d3.select("#compassG")
      .transition()
      .duration(200)
      .attr("transform","translate(0,30) rotate(-90)");
  }



  // Main Highway
  var sHighway = SHsvg.append("path")
            .datum(singleH.Path)
            .attr("d",d3.geoPath().projection(shprojection))
            .attr("stroke","gray")
            .attr("stroke-width",2)
            .attr("fill","none")
            .attr("class","singleHighwayMain");

  //Legs
  SHsvg.selectAll(".segmentLine")
    .data(singleH.Cities)
    .enter()
    .append("path")
      .attr("d",d3.geoPath().projection(shprojection))
      .attr("fill","none")
      .attr("cid", function(d,i){return (""+d.cid+"");})
      .attr("name", function(d,i){return (""+d.name+"");})
      .attr("class", function(d,i){return ("segmentLine segTo"+d.cid);});


  // Voronoi
  var shNodes = []
  d3.selectAll(".segmentLine")
    .each(function(d,ii){
      var pathInQuestion = d3.selectAll(".segmentLine").nodes()[ii];
      try{
        shNodes = shNodes.concat(SHsample(pathInQuestion,5,pathInQuestion.attributes["cid"].value,pathInQuestion.attributes["name"].value));
      }catch(e){
        // can't frickin figure out why this bombs once in a blue moon
        debug=0;
      }
    });
  var diagram = voronoi(shNodes);
  shcell = shcell.data(diagram.polygons())
  shcell.selectAll("path")
    .data(diagram.polygons())
    .enter().append("path")
      .attr("d", function(d) { return d ? "M" + d.join("L") + "Z" : null; })
      .style("stroke","none")
      .style("fill","#fff")
      .attr("class","shCells")
      .attr("cid",function(d,i){return (shNodes[i][2]);})
      .on("mouseover", shmouseover);

  // Text (on Top) :-P
  shcityText = SHsvg.append("text")
      .attr("x",0)
      .attr("y",0)
      .attr("class","shicityText")
      .text("");



});

// Useful Functions
function SHsample(pathNode, precision, cid, name) {
  var pathLength = pathNode.getTotalLength(),
      samples = [];
  for (var sample, sampleLength = 0; sampleLength <= pathLength; sampleLength += precision) {
    sample = pathNode.getPointAtLength(sampleLength);
    samples.push([sample.x, sample.y, cid, name]);
  }
  return samples;
}
function shmouseover(dd) {
  d3.selectAll(".segmentLine").style("stroke","#aaa").style("stroke-width","2");
  var mycid = d3.select(this).attr("cid");
  d3.selectAll(".segTo"+mycid).style("stroke","#69b93c").style("stroke-width","3");

  shcityText
    .attr("x",dd.data[0])
    .attr("y",dd.data[1])
    .attr("text-anchor",function(){
      if (dd.data[0]<SINGLEHIGHWAY.width/2){
        return "start";
      }else{
        return "end";
      }
    })
    .text(dd.data[3]);
}

// New Interstate is Selected
$('.singleHighwayDropDown').on('select2:select', function (evt) {
  // Do something
  var interstateID = $('.singleHighwayDropDown').val();
  //update the compass :-)
  d3.json(("./data/interstates/"+interstateID+".json"), function(error, singleH2) {
    if (error) throw error;
    var isNS = 0;
    if (singleH2.direction=="East"){
      isNS = 0;
      d3.select("#compassG")
        .transition()
        .duration(2000)
        .attr("transform","translate(0,0) rotate(0)");

    }else{
      isNS = 1;
      d3.select("#compassG")
        .transition()
        .duration(2000)
        .attr("transform","translate(0,30) rotate(-90)");
    }

    //*
    // delete the shit from previous interstate
    SHsvg.selectAll(".segmentLine")
        .classed("segmentsLeaving",true)
        .classed("segmentLine",false);
    SHsvg.selectAll(".segmentsLeaving")
        .style("opactiy",1)
        .transition()
        .duration(500)
        .style("opacity",0).remove();
    shcell.selectAll(".shCells").remove();
    SHsvg.selectAll(".shicityText")
        .classed("cityLeaving",true)
        .classed("shicityText",false);
    d3.selectAll(".cityLeaving").style("opactiy",1)
        .transition()
        .duration(500)
        .style("opacity",0).remove();
    //*/

    // Create Main Route
    SHsvg.selectAll("#dummypath")
        .remove();
    var dummy = SHsvg.append("path")
              .datum(singleH2.Path)
              .attr("d",d3.geoPath().projection(shprojection))
              .attr("stroke","none")
              .attr("stroke-width",0)
              .attr("fill","none")
              .attr("id","dummypath");
    SHsvg.select(".singleHighwayMain")
        .transition()
        .duration(2000)
        .attrTween('d', function(d){
          var prev = d3.select(this).attr('d');
          var curr = d3.select("#dummypath").attr('d');
          return d3.interpolatePath(prev,curr);
        });

    // Create Legs
    SHsvg.selectAll(".segmentLine")
      .data(singleH2.Cities)
      .enter()
      .append("path")
        .attr("d",d3.geoPath().projection(shprojection))
        .attr("fill","none")
        .attr("cid", function(d,i){return (""+d.cid+"");})
        .attr("name", function(d,i){return (""+d.name+"");})
        .style("opacity",0.0)
        .attr("class", function(d,i){return ("segmentLine segTo"+d.cid);})
        .transition()
        .delay(1500)
        .duration(500)
        .style("opacity",1);

    // Voronoi
    var shNodes = []
    d3.selectAll(".segmentLine")
      .each(function(d,ii){
        var pathInQuestion = d3.selectAll(".segmentLine").nodes()[ii];
        try{
          shNodes = shNodes.concat(SHsample(pathInQuestion,5,pathInQuestion.attributes["cid"].value,pathInQuestion.attributes["name"].value));
        }catch(e){
          // can't frickin figure out why this bombs once in a blue moon
          debug=0;
        }
      });
    if (shNodes.length>0){
      var diagram = voronoi(shNodes);
      shcell = shcell.data(diagram.polygons())
      shcell.selectAll("path")
        .data(diagram.polygons())
        .enter().append("path")
          .attr("d", function(d) { return d ? "M" + d.join("L") + "Z" : null; })
          .style("stroke","none")
          .style("fill","#fff")
          .attr("class","shCells")
          .attr("cid",function(d,i){return (shNodes[i][2]);})
          .on("mouseover", shmouseover);
          /*
          .transition()
          .delay(1500)
          .duration(500)
          .style("stroke","#eee"); */
      // Text (on Top) :-P
      shcityText = SHsvg.append("text")
          .attr("x",0)
          .attr("y",0)
          .attr("class","shicityText")
          .text("");
      d3.selectAll(".shicityText")
          .style("opacity",0)
          .transition()
          .delay(1500)
          .duration(500)
          .style("opacity",1);
    }


    //*/
    //*
    //*/
  });


});
