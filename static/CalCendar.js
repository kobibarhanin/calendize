jQuery.ajaxSettings.traditional = true;

instances_golbal = null;
floating_instances=[]
anchor_instances=[]

$(document).ready(function () {
    initiate([], new Date().toISOString().split("T")[0])
});

// '2018-12-26'
startDate=new Date(2018, 11, 23, 0, 0, 0, 0);
endDate=new Date(2018, 11, 29, 0, 0, 0, 0);

function initiate(events,defaultDate) {

    $('#rangestart').calendar({
        type: 'date',
        endCalendar: $('#rangeend'),
        onChange: function (date, text) {
            startDate = date;
        },
    });
    $('#rangeend').calendar({
        type: 'date',
        startCalendar: $('#rangestart'),
        onChange: function (date, text) {
            endDate = date;
        },
    });

    $('#calendar').fullCalendar({
    header: {
      left: 'prev,next today',
      center: 'title',
      right: 'month,agendaWeek,agendaDay,listWeek'
    },
    defaultDate: defaultDate,
    defaultView: 'agendaWeek',
    navLinks: true, // can click day/week names to navigate views
    editable: true,
    eventLimit: true, // allow "more" link when too many events
    events: events
  });



    $("#calc_button").click(function(){


        $.getJSON("/calculate",
                 {
                     _startDate: startDate.getTime(),
                     _endDate: endDate.getTime(),
                     _anchor_instances:arrayToString(anchor_instances),
                     _floating_instances:arrayToString(floating_instances),
                     _algorithm: $("#dd_algo option:selected").text()
                 },
                function(instances){
                    $('#calendar').empty();
                    $("#datepicker").after("<div id='calendar'></div>");

                    initiate(instances, startDate.toISOString().split("T")[0]);

          });
    });

    $("#fetch_button").click(function(){
        $.getJSON("/fetch",
             {
                _startDate: startDate.getTime(),
                _endDate: endDate.getTime()
             },
            function(instances){
                $('#calendar').empty();
                $("#datepicker").after("<div id='calendar'></div>");

                instances_golbal=instances;

                for(i=0; i<instances.length; i++){
                    $('#dd_anchor').append( new Option(instances[i]["title"],i));
                    $('#dd_floating').append( new Option(instances[i]["title"],i));
                }

                initiate(instances,startDate.toISOString().split("T")[0]);

        });
    });

}


function build_dd (dd,table_id) {
  var table = document.getElementById(table_id);
  var row = table.insertRow(table.rows.length);
  var cell1 = row.insertCell(0);
  var cell2 = row.insertCell(1);
  var cell3 = row.insertCell(2);
  var cell4 = row.insertCell(3);


  cell1.innerHTML = $(dd + ' option:selected').text();
  cell2.innerHTML = instances_golbal[$(dd + ' option:selected').val()]["id"];
  cell3.innerHTML = instances_golbal[$(dd + ' option:selected').val()]["start"];
  cell4.innerHTML = instances_golbal[$(dd + ' option:selected').val()]["end"];

  if (table_id=="anchor_table"){
      anchor_instances.push(instances_golbal[$(dd + ' option:selected').val()]["id"])
  }
  else {
      floating_instances.push(instances_golbal[$(dd + ' option:selected').val()]["id"])
  }

}


function arrayToString(array){
    res = ""
    for (i=0; i<array.length; i++){
        res+=array[i]+","
    }
    return res
}

