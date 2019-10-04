$('.item .title').click(function () {
    // $(this).next().toggleClass('hide')
    //
    // $(this).next().removeClass('hide');
    // $(this).parent().siblings().find('.body').addClass('hide');

    $(this).next().removeClass('hide').parent().siblings().find('.body').addClass('hide');
});
