// Dropdown Stuff
$(document).ready(function() {
  d3.json("./data/interstateList.json", function(error, io) {
    if (error) throw error;
    $(".singleHighwayDropDown").select2({
      data: io
    });
  });
});

// Actual Map Stuff
var SINGLEHIGHWAY = {'width': 0, 'height':0}
SINGLEHIGHWAY.width  = Number(d3.select("#singleHighwayMap").style("width").split("px")[0]);
SINGLEHIGHWAY.height = Number(d3.select("#singleHighwayMap").style("height").split("px")[0]);
SINGLEHIGHWAY.marginY = 80;
SINGLEHIGHWAY.marginX = 20;

// Draw the Compass
var SHsvg = d3.select("#singleHighwayMap").append("svg")
    .attr("width", SINGLEHIGHWAY.width)
    .attr("height", SINGLEHIGHWAY.height);
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



// Initialize the Viz
d3.json("./data/interstates/178.json", function(error, singleH) {
  if (error) throw error;

  var shX = d3.scaleLinear()
              .domain(  [
                          d3.min(singleH.Path, function(d) {return d.lon;}),
                          d3.max(singleH.Path, function(d) {return d.lon;})])
              .range([SINGLEHIGHWAY.marginX, SINGLEHIGHWAY.width-SINGLEHIGHWAY.marginX]);
  var shY = d3.scaleLinear()
              .domain(  [
                          d3.min(singleH.Path, function(d) {return d.lat;}),
                          d3.max(singleH.Path, function(d) {return d.lat;})])
              .range([SINGLEHIGHWAY.height-SINGLEHIGHWAY.marginY, SINGLEHIGHWAY.marginY]);
  SINGLEHIGHWAY.shLineFunction = d3.line()
            .x(function(d) { return shX(d.lon); })
            .y(function(d) { return shY(d.lat); });


  // Main Highway
  var sHighway = SHsvg.append("path")
            .attr("d", function(){return SINGLEHIGHWAY.shLineFunction(singleH.Path);} )
            .attr("stroke","gray")
            .attr("stroke-width",2)
            .attr("fill","none")
            .attr("class","singleHighwayMain");


  // Arrows
  SINGLEHIGHWAY.path = d3.select(".singleHighwayMain");
  SINGLEHIGHWAY.str = SINGLEHIGHWAY.path.attr("d");
  SINGLEHIGHWAY.length = SINGLEHIGHWAY.path.node().getTotalLength();
  console.log(SINGLEHIGHWAY)
  /*
  SHsvg.selectAll(".segmentLine")
    .data(d3.range(16))
    //.data(singleH.Cities.With)
    .enter()
    .append("g")
      .attr("class", "segmentLine")
      .each(draw);
  */
  var isNS = 0;
  SHsvg.selectAll(".segmentLineWith")
    .data(singleH.Cities.With)
    .enter()
    .append("g")
      .attr("class", "segmentLineWith segmentLine")
      .attr("id", function(d,i){return ("segmentLineWith_"+i);})
      .each(function(d,i){return drawSeg(d,i,1,singleH.Path,shX,shY,isNS);});
  //*
  SHsvg.selectAll(".segmentLineAgainst")
    .data(singleH.Cities.Against)
    .enter()
    .append("g")
      .attr("class", "segmentLineAgainst segmentLine")
      .attr("id", function(d,i){return ("segmentLineAgainst_"+i);})
      .each(function(d,i){return drawSeg(d,i,-1,singleH.Path,shX,shY,isNS);});
  //*/


});




function drawSeg(d,i,s,p,shXX,shYY,isNS) {

    if (s>0){
      var g = d3.select("#segmentLineWith_"+i);
    }else{
      var g = d3.select("#segmentLineAgainst_"+i);
    }

    var offset = [
          s*0*5 + 10 * 0,
          s*1*5 + 10 * s * d.layer
        ];
    var pStart = d.StartIndex;
    var pStop  = d.StopIndex;

    var pseg = p.slice(d3.min([pStart,pStop]), d3.max([pStart,pStop]));

    g.attr("transform", "translate(" + (offset) + ")")
      .append("path")
        .attr("title",d.Name)
        .style("opacity",0)
        .attr("d", function(){return SINGLEHIGHWAY.shLineFunction(pseg);} )
          .transition()
          .delay(2000)
          .duration(200)
          .style("opacity",1);

    var myTextAnchor = 'end';
    if (s<0){
      myTextAnchor = 'start';
    }
    if (i<3){
      //*
      if (isNS){
        var myX = p[pStop].lat;
        var myY = p[pStop].lon;
        g.append("text")
          .style("opacity",0)
          .attr("class","singleHighwayLabel")
          .attr("x",shXX(myX))
          .attr("y",shYY(myY)+8*s+4)
          .text(d.cityName)
          .attr("text-anchor",myTextAnchor)
          .transition()
          .delay(2000)
          .duration(200)
          .style("opacity",1);
      }else{
        var myY = p[pStop].lat;
        var myX = p[pStop].lon;
        g.append("text")
        .style("opacity",0)
          .attr("class","singleHighwayLabel")
          .attr("x",shXX(myX))
          .attr("y",shYY(myY)+6*s+4)
          .text(d.cityName)
          .attr("text-anchor",myTextAnchor)
          .transition()
          .delay(2000)
          .duration(200)
          .style("opacity",1);
      }


        //*/
    }
    /*
    g.append("use")
      .attr("xlink:href", "#arrowhead")
      .attr("transform", "translate(" + end + ") rotate(" + (endAngle * 180 / Math.PI) + ")");
    */
  }

/*
function draw(d) {

    var g = d3.select(this),
        l = 20 + SINGLEHIGHWAY.length * d / 16,
        angle = angleAtLength(l),
        end = pointAtLength(l + 20),
        endAngle = angleAtLength(l + 20),
        offset = [
          12 * Math.cos(angle - Math.PI / 2),
          12 * Math.sin(angle - Math.PI / 2)
        ];

    g.attr("transform", "translate(" + (offset) + ")")
      .append("path")
        .attr("d", SINGLEHIGHWAY.str)
        .attr("stroke-dasharray", "0," + Math.max(0, l - 20) + ",40," + SINGLEHIGHWAY.length);
  }
*/


function pointAtLength(l) {
    var xy = SINGLEHIGHWAY.path.node().getPointAtLength(l);
    return [xy.x, xy.y];
}
// Approximate tangent
function angleAtLength(l) {
  var a = pointAtLength(Math.max(l - 0.01,0)), // this could be slightly negative
      b = pointAtLength(l + 0.01); // browsers cap at total length
  return Math.atan2(b[1] - a[1], b[0] - a[0]);
}




$('.singleHighwayDropDown').on('select2:select', function (evt) {
  // Do something
  var interstateID = $('.singleHighwayDropDown').val();
  d3.json(("./data/interstates/"+interstateID+".json"), function(error, singleH2) {
    if (error) throw error;
    var isNS = 0;
    if (singleH2.direction=="East"){
      isNS = 0;
      var shX = d3.scaleLinear()
                  .domain(  [
                              d3.min(singleH2.Path, function(d) {return d.lon;}),
                              d3.max(singleH2.Path, function(d) {return d.lon;})])
                  .range([SINGLEHIGHWAY.marginX, SINGLEHIGHWAY.width-SINGLEHIGHWAY.marginX]);
      var shY = d3.scaleLinear()
                  .domain(  [
                              d3.min(singleH2.Path, function(d) {return d.lat;}),
                              d3.max(singleH2.Path, function(d) {return d.lat;})])
                  .range([SINGLEHIGHWAY.height-SINGLEHIGHWAY.marginY, SINGLEHIGHWAY.marginY]);
      SINGLEHIGHWAY.shLineFunction = d3.line()
                .x(function(d) { return shX(d.lon); })
                .y(function(d) { return shY(d.lat); });
      d3.select("#compassG")
        .transition()
        .duration(2000)
        .attr("transform","translate(0,0) rotate(0)");

    }else{
      isNS = 1;
      var shX = d3.scaleLinear()
                  .domain(  [
                              d3.max(singleH2.Path, function(d) {return d.lat;}),
                              d3.min(singleH2.Path, function(d) {return d.lat;})])
                  .range([SINGLEHIGHWAY.marginX, SINGLEHIGHWAY.width-SINGLEHIGHWAY.marginX]);
      var shY = d3.scaleLinear()
                  .domain(  [
                              d3.min(singleH2.Path, function(d) {return d.lon;}),
                              d3.max(singleH2.Path, function(d) {return d.lon;})])
                  .range([SINGLEHIGHWAY.height-SINGLEHIGHWAY.marginY, SINGLEHIGHWAY.marginY]);
      SINGLEHIGHWAY.shLineFunction = d3.line()
                .x(function(d) { return shX(d.lat); })
                .y(function(d) { return shY(d.lon); });
      d3.select("#compassG")
        .transition()
        .duration(2000)
        .attr("transform","translate(0,30) rotate(-90)");
    }

    /*
    SHsvg.select(".singleHighwayMain")
        .transition()
        .duration(2000)
        .attr("d", function(){return SINGLEHIGHWAY.shLineFunction(singleH2.Path);} );
    */
    //*
    SHsvg.selectAll(".segmentLineAgainst")
        .remove();
    SHsvg.selectAll(".segmentLineWith")
        .remove();
    //*/
    SHsvg.select(".singleHighwayMain")
        .transition()
        .duration(2000)
        .attrTween('d', function(d){
          var prev = d3.select(this).attr('d');
          var curr = SINGLEHIGHWAY.shLineFunction(singleH2.Path);
          return d3.interpolatePath(prev,curr);
        });

    //*
    SHsvg.selectAll(".segmentLineWith")
      .data(singleH2.Cities.With)
      .enter()
      .append("g")
        .attr("class", "segmentLineWith segmentLine")
        .attr("id", function(d,i){return ("segmentLineWith_"+i);})
        .each(function(d,i){return drawSeg(d,i,1,singleH2.Path,shX,shY,isNS);});
    //*/
    //*
    SHsvg.selectAll(".segmentLineAgainst")
      .data(singleH2.Cities.Against)
      .enter()
      .append("g")
        .attr("class", "segmentLineAgainst segmentLine")
        .attr("id", function(d,i){return ("segmentLineAgainst_"+i);})
        .each(function(d,i){return drawSeg(d,i,-1,singleH2.Path,shX,shY,isNS);});
    //*/
  });


});










/*
{
  "LongName": "hello",
  "ShortName": "hi",
  "Number": 55,
  "Width_EW_km": 100,
  "Height_NS_km": 1000,
  "Path": [
    {"id": 10127, "indx": 0, "lat": 41.2, "lon": -84.2},
    {"id": 10128, "indx": 1, "lat": 41.3, "lon": -84.1}
  ],
  "Cities": {
    "With": [
      {"Name": "Chicago", "id": 10123, "StartIndx": 0, "StopIndx": 1, "layer": 0},
      {"Name": "St Louis", "id": 10125, "StartIndx": 0, "StopIndx": 1, "layer": 1}
    ],
    "Against": [
      {"Name": "Chicago", "id": 10123, "StartIndx": 0, "StopIndx": 1, "layer": 1},
      {"Name": "St Louis", "id": 10125, "StartIndx": 0, "StopIndx": 1, "layer": 0}
    ]
  }
}
*/
