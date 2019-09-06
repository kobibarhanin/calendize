jQuery.ajaxSettings.traditional = true;

instances_golbal = null;
instances_golbal_mapping = {};

floating_instances=[];
anchor_instances=[];

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

    $("#dev_button").unbind('click').click(function(){

        for (var i=0; i< instances_golbal.length; i++){
            title = instances_golbal[i]['title']
            console.log(title)
            if (title.includes('Anc')){
                add_to_row_table(instances_golbal[i], 'anchor_table')
                $('#row_'+instances_golbal[i]['id']).remove();
            }
            else if (title.includes('Flt')){
                add_to_row_table(instances_golbal[i], 'floating_table')
                $('#row_'+instances_golbal[i]['id']).remove();
            }
        }
    });

    $("#calc_button").unbind('click').click(function(){


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
                    initiate(instances,endDate.toISOString().split("T")[0]);
          });
    });

    $("#fetch_button").unbind('click').click(function(){
        $.getJSON("/fetch",
             {
                _startDate: startDate.getTime(),
                _endDate: endDate.getTime()
             },
            function(instances){
                $('#calendar').empty();
                $("#datepicker").after("<div id='calendar'></div>");


                instances_golbal=instances;
                for (var i=0; i< instances_golbal.length; i++){
                   instances_golbal_mapping[instances_golbal[i]['id']]=i;
                }


                for(i=0; i<instances.length; i++){
                    $('#dd_anchor').append( new Option(instances[i]["title"],i));
                    $('#dd_floating').append( new Option(instances[i]["title"],i));
                }

                initiate(instances,endDate.toISOString().split("T")[0]);
                build_table(instances_golbal,'events_table')

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


function build_table (entries,table_id) {
    var table = document.getElementById(table_id);
    entries.forEach(function(entry){
        var row = table.insertRow(table.rows.length);
        row.id = "row_"+entry["id"];
        var cell1 = row.insertCell(0);
        var cell2 = row.insertCell(1);
        var cell3 = row.insertCell(2);
        var cell4 = row.insertCell(3);
        var cell5 = row.insertCell(4);
        cell1.innerHTML = entry['title'];
        cell2.innerHTML = entry["id"];
        cell3.innerHTML = entry["start"];
        cell4.innerHTML = entry["end"];
        cell5.innerHTML = "<input id="+entry['id']+" type='checkbox' name="+entry['id']+" value='some_value'>"
    });
}

function add_selected_to_table(table_id) {
    for (var i=0; i< instances_golbal.length; i++){
        if($('#'+instances_golbal[i]['id']).is(':checked')){
            add_to_row_table(instances_golbal[i],table_id)
            $('#row_'+instances_golbal[i]['id']).remove();
        }
    }
}

function add_to_row_table(entry,table_id) {
    var table = document.getElementById(table_id);
    var row = table.insertRow(table.rows.length);
    row.id = "row_"+entry["id"];
    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);
    var cell3 = row.insertCell(2);
    var cell4 = row.insertCell(3);
    cell1.innerHTML = entry['title'];
    cell2.innerHTML = entry["id"];
    cell3.innerHTML = entry["start"];
    cell4.innerHTML = entry["end"];

    if (table_id === "anchor_table"){
        let idx = instances_golbal_mapping[entry["id"]];
        anchor_instances.push(instances_golbal[idx])
    }
    else {
        let idx = instances_golbal_mapping[entry["id"]];
        floating_instances.push(instances_golbal[idx])
    }
}


function arrayToString(array){
    res = "";
    for (i=0; i<array.length; i++){
        res += array[i]["id"]+","
    }
    return res
}

