// Global visibility Stuff
GlobalVizView = {"header": true, "simViz":true};

function whichVizAreInView(){

  var divTop = document.getElementById("headerSection").getBoundingClientRect().top;
  var divBot = document.getElementById("headerSection").getBoundingClientRect().bottom;
  var inView = (divTop<window.innerHeight) && (divBot>0);
  if ((GlobalVizView.header==false)&(inView)){
    // just came into view
    GlobalVizView.header = inView;
    visit();
  }else{
    GlobalVizView.header = inView;
  }

  var divTop = document.getElementById("simVizAnchorDiv").getBoundingClientRect().top;
  var divBot = document.getElementById("simVizAnchorDiv").getBoundingClientRect().bottom;
  var inView = (divTop<window.innerHeight) && (divBot>0) && (divBot-divTop>100);
  if ((GlobalVizView.simViz==false)&(inView)){
    // just came into view
    GlobalVizView.simViz = inView;
    //visit();
  }else{
    GlobalVizView.simViz = inView;
  }
}


window.onresize = function(event) {
  whichVizAreInView();
  updateScaling();
}
window.onscroll = function(event){
  whichVizAreInView();
}


function updateScaling(){
  // HEADER

  // SINGLE HIGHWAY

  // BAR GRAPH

  // Too lazy for now... how about overflow: hidden
}
