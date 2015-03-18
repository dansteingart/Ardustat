//calibration functions
console.log('calibration functions is here');

/*when button clicked 
- send ajax request to server. server sets the ardustat id, and checks to see if there is a resistance table.
if there is a resistance table
- tell user, ask to do calibration anyway
if there isnt
- tell user, insist on calibration

// for now - send message - receive response. TODO urgent - work out why not getting response from server, look up ajax docs.
// then go onto calibration.
*/
//channel = 'ch1'
var ardustat_id;
$('#ardustat_id_submit').click(function() {
  console.log('ardustat_input clicked');
  var form = $('#ardustat_input');
  ardustat_data = form.serializeObject();
  ardustat_id = ardustat_data['ardustat_id'];
  datasend = {"ardustat_id_setter":ardustat_id};
  console.log('datasend is ' + datasend);
  $.ajax({
    type:'POST',
    url:'/senddata',
    async: true,
    data: datasend,  
    })
    .done(function( data ) {
        console.log('and here is the data '+data);
        if (data == "res_table is here") goRes_table_here()
        else goRes_table_not_here()
    })
    .fail(function( jqXHR, textStatus, errorThrown ) {
      console.log('something went wrong');
      console.log(jqXHR);
      console.log(textStatus);
      console.log(errorThrown);
    });
    return false;
  
  });

function goRes_table_here() {
  console.log('res_table_here called');
  $("#yes_resistance_table").show()
  //$('#ardustat_id_display').text("Ardustat Id is "+ardustat_id.toString() );
  $('#ardustat_input_div').hide()
  $('#calibration_instructions').show()
 }
 
function goRes_table_not_here() {
  console.log('res_table_not_here called');
  $("#no_resistance_table").show()
  //$('#ardustat_id_display').text("Ardustat Id is "+ardustat_id.toString() );
  $('#arudstat_input_div').hide()
  $('#calibration_instructions').show()
}

//TODO: Check that this stuff works. 
$("#calibrate").click(function() {
  console.log('#calibrate clicked');
  goCalibrationProgress();
  var form = $('#ardustat_input');
  DataToSend = form.serializeObject();
  resistor_value = $('#resistor_value').val()
  console.log('resistor value is ' + resistor_value);  //TODO: error checking - if user enters 10,000 won't know that something hasn't worked. wow this stuff is truly a pain in the ass...
  DataToSend['resistor_value'] = resistor_value;
  console.log(DataToSend);
  $.ajax({
    type:'POST',
    url:'/senddata',
    async: true,
    data: DataToSend,
    })
    .done(function( data ) {
      console.log('something worked');
    })
    .fail(function( jqXHR, textStatus, errorThrown ) {
    console.log('something went wrong');
    console.log(jqXHR);
    console.log(textStatus);
    console.log(errorThrown);
    });
  return false;
});


function goCalibrationProgress() 
{
  console.log('goCalibrationProgess called');
  $('#calibration_instructions').hide();
  $('#calibration_progress').show();
  console.log('this finished');
}


function goCalibrationFinished()
{
  console.log('goCalibrationFinished called');
  $('#calibration_progress').hide()
  $('#calibration_finished').show()
}


$.fn.serializeObject = function()
{
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    o['type_of_experiment'] = 'calibration';
    o['channel'] = channel;
    return o;
};

/*
$('form').submit(function(){
  socket.emit('chat message', $('#m').val());
  $('#m').val('');
  return false;
});
*/


