window.onload = function () {
    const tranferForm = document.querySelector('.tranfer-form');
    if (tranferForm) {
        const srcUserSelect = tranferForm.querySelector('.tranfer-form select[name="src_user"]');
        const dstInnInput = tranferForm.querySelector('.tranfer-form input[name="dst_inn"]');
        const amountInput = tranferForm.querySelector('.tranfer-form input[name="amount"]');
        const makeTransferButton = tranferForm.querySelector('.tranfer-form input[type="submit"]');

        let srcUserSelectHelpText = createHelpText(srcUserSelect);
        let dstInnInputHelpText = createHelpText(dstInnInput);
        let amountInputHelpText = createHelpText(amountInput);

        let srcUser;
        let dstUsersFound = false;

        srcUserSelect.onclick = function (e) {
            srcUserSelectHelpText.innerHTML = '';
        };
        srcUserSelect.onchange = function (e) {
            const pk = e.target.value;
            if (!pk.match(/\d+/)) {
                return;
            }
            const xhr = new XMLHttpRequest();
            xhr.open('GET', '/api/users/' + pk);
            xhr.onload = function () {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    srcUser = JSON.parse(xhr.responseText);
                }
            };
            xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
            xhr.send(null);
        };

        dstInnInput.onblur = function (e) {
            const inn = e.target.value;
            if (inn.length < 1) {
                return
            }

            if (!inn.match(/\d{12}/)) {
                dstInnInputHelpText.innerHTML = ' введите ИНН, состоящий из 12 цифр';
                return
            }
            const xhr = new XMLHttpRequest();
            xhr.open('GET', '/api/users?inn=' + inn);
            xhr.onload = function () {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    const foundUsers = JSON.parse(xhr.responseText);
                    if (foundUsers.length === 0) {
                        dstInnInputHelpText.innerHTML = ' пользователи с указанным ИНН не найдены';
                        dstInnInput.placeholder = inn;
                        dstInnInput.value = '';
                    } else {
                        dstUsersFound = true;
                        dstInnInputHelpText.innerHTML = '';
                    }
                }
            };
            xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
            xhr.send(null);
        };

        amountInput.onclick = function (e) {
            amountInputHelpText.innerHTML = '';
        };

        makeTransferButton.onclick = function (e) {
            amountInputHelpText.innerHTML = '';

            if (!srcUser) {
                srcUserSelectHelpText.innerHTML = ' не выбран отправитель';
                srcUserSelect.focus();
                return false;
            }

            if (!dstUsersFound) {
                dstInnInputHelpText.innerHTML = ' не найдены получатели';
                dstInnInput.focus();
                return false;
            }

            let amount = parseFloat(amountInput.value);
            if (isNaN(amount) || amount === 0) {
                amountInputHelpText.innerHTML = ' необходимо ввести сумму перевода';
                amountInput.focus();
                return false;
            }

            if (amount > parseFloat(srcUser.balance)) {
                amountInputHelpText.innerHTML = ' недостаточно средств на счете отправителя';
                amountInput.focus();
                return false;
            }

            // return true;
        };
    }

    function createHelpText(parent) {
        let helpText = document.createElement('span');
        helpText.classList.add('helptext');
        helpText.innerHTML = '';
        parent.parentNode.appendChild(helpText);
        return helpText;
    }
};
