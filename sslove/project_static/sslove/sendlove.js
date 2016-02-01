
function makeAutocomplete(data) {

    // Overrides the default autocomplete filter function to search only from the beginning of the string
    $.ui.autocomplete.filter = function (array, term) {
        var matcher = new RegExp("^" + $.ui.autocomplete.escapeRegex(term), "i");
        return $.grep(array, function (value) {
            return matcher.test(value.label || value.value || value);
        });
    };

    $('.recipient-input').autocomplete({
        source: data,       
        select: function(event, ui) { 
            console.log(ui.item);
            $('.recipient_id').attr('value', ui.item['id']);               
            $('.text-area').focus();
        },
        options: {
            delay: 0,
        }
    })

    var selectFunction = function(event, ui) {
        console.log(ui.item);
        $('.recipient_id').attr('value', ui.item['id']);               
        $(textarea).focus();
    };

    var checkName = function() {
        console.log("HEY");
        var name = $('.recipient-input').val();
        console.log(name);
        for (var user in data) {
            console.log(data[user])
            if (data[user]['value'] === name) {
                $('.recipient_id').attr('value', data[user]['id']);               
            }
        }
    };

    $('.recipient-input').focusout(checkName.bind(this));

    $('.sendlove-form').submit(function() {
        checkName(); 
        return true;
    }.bind(this));
};
