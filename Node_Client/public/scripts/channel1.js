console.log('channel1 script called');

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
        if (data == "res_table is here") goRes_table_here_channel1()
        else goRes_table_not_here_channel1()
    })
    .fail(function( jqXHR, textStatus, errorThrown ) {
      console.log('something went wrong');
      console.log(jqXHR);
      console.log(textStatus);
      console.log(errorThrown);
    });
  return false;
});

function goRes_table_here_channel1()
{
  console.log('goRes table here called');
  $('#ardustat_input').hide()
  $('#yes_res_table').show()
}

function goRes_table_not_here_channel1()
{
  console.log('goRes table not here called');
  $('#ardustat_input').hide()
  $('#no_res_table').show()
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
    return o;
};
