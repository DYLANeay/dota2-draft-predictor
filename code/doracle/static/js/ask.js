// Ask the Oracle one question. There is no follow-up: every Send is independent.

$(document).ready(function () {
    const askButton = $("#askBtn");
    const questionInput = $("#questionInput");
    const output = $("#outputOracle");

    function ask() {
        const question = questionInput.val().trim();
        if (!question) {
            output.val("Type a question first.");
            return;
        }

        askButton.prop("disabled", true).text("Oracle is thinking...");
        output.val("");

        $.ajax({
            type: "POST",
            url: "/api/ask",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                "question": question,
                "radiant": draft.radiant,
                "dire": draft.dire,
                "radiant_bans": draft.radiant_bans,
                "dire_bans": draft.dire_bans
            }),
            dataType: "json"
        })
            .done(function (data) {
                output.val(data.answer);
                questionInput.val("");
            })
            .fail(function (xhr) {
                const body = xhr.responseJSON || {};
                output.val("Error: " + (body.error || xhr.statusText));
            })
            .always(function () {
                askButton.prop("disabled", false).text("Send");
            });
    }

    askButton.click(ask);

    // Ctrl/Cmd+Enter also sends.
    questionInput.keydown(function (event) {
        if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
            ask();
        }
    });
});
