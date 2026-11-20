// The draft currently on screen. ask.js sends this along with every question.
const draft = {
    radiant: [],
    dire: [],
    radiant_bans: [],
    dire_bans: [],
};

const MAX_PICKS = 5;
const MAX_BANS = 7;

$(document).ready(function () {

    /*
    ======================================
    PICK / BAN EVENTS
    ======================================
    */

    // Click a hero and pick it, or shift-click it to ban it.
    $(".hero-select-left").click(function (event) {
        select_hero("radiant", $(this).data("heroid"), event.shiftKey);
    })

    $(".hero-select-right").click(function (event) {
        select_hero("dire", $(this).data("heroid"), event.shiftKey);
    })

    // Click a filled slot to clear it again.
    $(".hero-pool-radiant").click(function () {
        remove_hero(draft.radiant, $(this).data("heroid"));
    })

    $(".hero-pool-dire").click(function () {
        remove_hero(draft.dire, $(this).data("heroid"));
    })

    $(".hero-pool-ban-radiant").click(function () {
        remove_hero(draft.radiant_bans, $(this).data("heroid"));
    })

    $(".hero-pool-ban-dire").click(function () {
        remove_hero(draft.dire_bans, $(this).data("heroid"));
    })

    /*
    ======================================
    BUTTON EVENTS
    ======================================
    */

    let output_box = $("#outputOracle")

    $("#suggestBtn1").click(function () {
        $.ajax({
            type: "POST",
            url: "/suggest1",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                "radiant": draft.radiant,
                "dire": draft.dire
            }),
            dataType: "json",
            success: function (data) {
                let pretty_data = JSON.stringify(data, undefined, 4)
                output_box.val(pretty_data)
                setHeight(output_box)

            }
        });
    })

    $("#suggestBtn2").click(function () {
        $.ajax({
            type: "POST",
            url: "/suggest2",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                "radiant": draft.radiant,
                "dire": draft.dire
            }),
            dataType: "json",
            success: function (data) {
                let pretty_data = JSON.stringify(data, undefined, 4)
                output_box.val(pretty_data)
                setHeight(output_box)

            }
        });
    })


    $("#suggestBtn3").click(function () {
        $.ajax({
            type: "POST",
            url: "/suggest3",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                "radiant": draft.radiant,
                "dire": draft.dire
            }),
            dataType: "json",
            success: function (data) {
                let pretty_data = JSON.stringify(data, undefined, 4)
                output_box.val(pretty_data)
                setHeight(output_box)

            }
        });
    })


});

function select_hero(side, hero_id, ban) {
    if (hero_id === -1 || hero_id === undefined) {
        return;
    }

    if (ban) {
        add_to_pool(draft[side + "_bans"], hero_id, MAX_BANS);
    } else {
        add_to_pool(draft[side], hero_id, MAX_PICKS);
    }

    sync_images();
}

function remove_hero(pool, hero_id) {
    if (hero_id === -1 || hero_id === undefined) {
        return;
    }

    remove_from_pool(pool, hero_id);
    sync_images();
}

function is_used(hero_id) {
    return Object.values(draft).some(pool => pool.includes(hero_id));
}

function add_to_pool(pool, hero_id, max) {
    if (!is_used(hero_id) && pool.length < max) {
        pool.push(hero_id);
    }
}

function remove_from_pool(pool, hero_id) {
    let idx = pool.indexOf(hero_id);
    if (idx > -1) {
        pool.splice(idx, 1);
    }
}

function refresh_images() {
    $(".hero-pool").each(function () {
        $(this).attr("src", "/static/img/placeholder.png")
        $(this).css("height", "")
        $(this).data("heroid", -1);

    })
}

function update_images(faction, pool) {
    let imgs = $(`.hero-pool-${faction}`)

    for (const [i, hero_id] of pool.entries()) {
        $(imgs[i]).attr("src", `/static/img/avatar-sb/${hero_id.toString()}.png`)
        $(imgs[i]).css("height", "60px")
        $(imgs[i]).data("heroid", hero_id)

    }

}

function sync_images() {
    refresh_images()
    update_images("radiant", draft.radiant)
    update_images("dire", draft.dire)
    update_images("ban-radiant", draft.radiant_bans)
    update_images("ban-dire", draft.dire_bans)
}

function setHeight(jq_in) {
    jq_in.each(function (index, elem) {
        // works with pure javascript
        elem.style.height = elem.scrollHeight + 'px';
    });
}
