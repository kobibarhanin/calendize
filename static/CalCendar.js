jQuery.ajaxSettings.traditional = true;

instances_golbal = null;
instances_golbal_mapping = {};

floating_instances=[];
anchor_instances=[];
opportune_instances=[];
routine_instances=[];

calendar_instances=[];



$(document).ready(function () {
    initiate([], new Date().toISOString().split("T")[0], true)
});

// '2018-12-26'
startDate=new Date(2018, 11, 23, 0, 0, 0, 0);
endDate=new Date(2018, 11, 29, 0, 0, 0, 0);

function initiate(events, defaultDate, first) {

    if (first){
        $("#routine_populated").hide()
        $("#opportune_populated").hide()
        $("#floating_populated").hide()
        $("#anchor_populated").hide()
        $("#events_populated").hide()
    }

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

    $('#routine_from_calendar').calendar();

    $('#routine_to_calendar').calendar();

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
    events: events,


    });

    if (window.innerWidth < 768 ) {
        $('#calendar').fullCalendar('changeView', 'agendaDay');

    }

    $("#dev_button").unbind('click').click(function(){
        for (var i=0; i< instances_golbal.length; i++){
            title = instances_golbal[i]['title']
            console.log(title)
            if (title.includes('Anc')){
                $('#row_'+instances_golbal[i]['id']).remove();
                add_to_row_table(instances_golbal[i], 'anchor_table')
            }
            else if (title.includes('Flt')){
                $('#row_'+instances_golbal[i]['id']).remove();
                add_to_row_table(instances_golbal[i], 'floating_table')
            }
            else if (title.includes('Opp')){
                $('#row_'+instances_golbal[i]['id']).remove();
                add_to_row_table(instances_golbal[i], 'opportune_table')
            }
        }

        $("#routine_title").val("Routine")
        $("#routine_duration").val("1:30")
        $("#routine_from").val("December 23, 2018 4:00 PM")
        $("#routine_to").val("December 28, 2018 10:00 PM")

    });

    $("#calc_button").unbind('click').click(function(){
        $("#calc_button").addClass("loading");
        $.getJSON("/calculate",
                 {
                     _startDate: startDate.getTime(),
                     _endDate: endDate.getTime(),
                     _anchor_instances:arrayToString(anchor_instances),
                     _floating_instances:arrayToString(floating_instances),
                     _opportune_instances:arrayToString(opportune_instances),
                     _routine_instances:routienArrayToString(routine_instances),
                     _algorithm: $("#dd_algo option:selected").text()
                 },
                function(instances){
                    $('#calendar').empty();
                    $("#datepicker").after("<div id='calendar' style='max-width: none'></div>");
                    calendar_instances = instances
                    $("#calc_button").removeClass("loading");
                    initiate(instances,endDate.toISOString().split("T")[0], false);
                    $("html, body").animate({ scrollTop: 0 }, "slow");
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
                $("#datepicker").after("<div id='calendar' style='max-width: none'></div>");


                instances_golbal=instances;
                for (var i=0; i< instances_golbal.length; i++){
                   instances_golbal_mapping[instances_golbal[i]['id']]=i;
                }

                switcher("events_populated","events_default")
                initiate(instances,endDate.toISOString().split("T")[0], false);
                build_table(instances_golbal,'events_table')
        });
    });

    $("#routine_button").unbind('click').click(function(){

        switcher("routine_populated","routine_default")

        time_from = new Date($("#routine_from").val()).getTime()/1000
        time_to = new Date($("#routine_to").val()).getTime()/1000

        title = $('#routine_title').val();
        duration = $('#routine_duration').val();

        var table = document.getElementById('routine_table');
        var row = table.insertRow(table.rows.length);
        row.id = title+"_"+Math.random().toString(36).substring(7);
        var cell1 = row.insertCell(0);
        var cell2 = row.insertCell(1);
        var cell3 = row.insertCell(2);
        var cell4 = row.insertCell(3);
        var cell5 = row.insertCell(4);

        cell1.innerHTML = title
        cell2.innerHTML = duration
        cell3.innerHTML = new Date(time_from*1000).toISOString()
        cell4.innerHTML = new Date(time_to*1000).toISOString()
        cell5.innerHTML = "<input id=cb_"+row.id+" type='checkbox' name=cb_"+title+duration+" value='some_value'>"

        var routine_instance = {
            "id": row.id,
            "title": title,
            "duration": duration,
            "time_from": time_from,
            "time_to": time_to
        }

        routine_instances.push(routine_instance)
    });

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
            $('#row_'+instances_golbal[i]['id']).remove();
            add_to_row_table(instances_golbal[i],table_id)
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
    var cell5 = row.insertCell(4);
    cell1.innerHTML = entry['title'];
    cell2.innerHTML = entry["id"];
    cell3.innerHTML = entry["start"];
    cell4.innerHTML = entry["end"];
    cell5.innerHTML = "<input id="+entry['id']+" type='checkbox' name="+entry['id']+" value='some_value'>"


    if (table_id === "anchor_table"){
        switcher("anchor_populated","anchor_default")
        let idx = instances_golbal_mapping[entry["id"]];
        anchor_instances.push(instances_golbal[idx])
    }
    else if (table_id === "floating_table") {
        switcher("floating_populated","floating_default")
        let idx = instances_golbal_mapping[entry["id"]];
        floating_instances.push(instances_golbal[idx])
    }
    else if (table_id === "opportune_table") {
        switcher("opportune_populated","opportune_default")
        let idx = instances_golbal_mapping[entry["id"]];
        opportune_instances.push(instances_golbal[idx])
    }
}


function remove_selected(table_id) {

    console.log('removing from: ' +table_id)

    if (table_id == 'anchor_table')
        clear_list = anchor_instances
    else if (table_id == 'floating_table')
        clear_list = floating_instances
    else if (table_id == 'opportune_table')
        clear_list = opportune_instances

    for (var i=0; i< clear_list.length; i++){
        if($('#'+clear_list[i]['id']).is(':checked')){
            console.log('removing' + clear_list[i]['id'] + 'from: ' + table_id)
            $('#row_'+clear_list[i]['id']).remove();
            add_to_row_table(clear_list[i],'events_table')
        }
    }

    if (opportune_instances.length == 0){
        switcher("opportune_default", "opportune_populated")
    }
    if (floating_instances.length == 0){
        switcher("floating_default", "floating_populated")
    }
    if (anchor_instances.length == 0){
        switcher("anchor_default", "anchor_populated")
    }
}


function remove_selected_routing() {

    console.log('removing from routine_table')

    for (var i=0; i< routine_instances.length; i++){
        if($('#cb_'+routine_instances[i]['id']).is(':checked')){
            console.log('removing ' + routine_instances[i]['id'])
            $('#'+routine_instances[i]['id']).remove();
            routine_instances.splice(i, 1);
        }
    }

    if (routine_instances.length == 0){
        switcher("routine_default", "routine_populated")
    }


}

function arrayToString(array){
    res = "";
    for (i=0; i<array.length; i++){
        res += array[i]["id"]+","
    }
    return res
}

function routienArrayToString(array){
    res = "";
    for (i=0; i<array.length; i++){
        res += array[i]["title"]+";"+array[i]["duration"]+";"+array[i]["time_from"]+";"+array[i]["time_to"]+","
    }
    return res
}

function switcher(on, off){
    $("#"+off).hide()
    $("#"+on).show()
}
