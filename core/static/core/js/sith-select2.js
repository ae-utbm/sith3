/**
 * @typedef Select2Object
 * @property {number} id
 * @property {string} text
 */


/**
 * @typedef Select2Options
 * @property {Element} element
 * @property {Object} data_source
 * @property {number[]} excluded A list of ids to exclude from search
 */


/**
 * @param {Select2Options} options
 */
function sithSelect2(options) {
    return $(options.element).select2({
        theme: "classic",
        minimumInputLength: 2,
        ...options.data_source,
    })
}


/**
 * Build a data source for a Select2 from a local array
 * @param {Select2Object[]} source The array containing the data
 * @param {(function(): number[]) | undefined} excluded The ids to exclude from the search
 */
function local_data_source(source, excluded) {
    if (!!excluded) {
        const ids = excluded();
        return {data: source.filter((i) => !ids.includes(i.id))};
    }
    return {data: source};
}


/**
 * @typedef RemoteSourceOptions
 * @property {function(): number[]} excluded
 *        A callback to the ids to exclude from the search
 * @property {function(Object): Select2Object} result_converter
 *        A callback to the ids to exclude from the search
 */

/**
 * Build a data source for a Select2 from a remote url
 * @param {string} source The url of the endpoint
 * @param {RemoteSourceOptions} options
 */
function remote_data_source(source, options) {
    jQuery.ajaxSettings.traditional = true;
    let params = {
        url: source,
        dataType: "json",
        cache: true,
        delay: 250,
        data: function (params) {
            console.log(this.val())
            return {
                search: params.term,
                exclude: [
                    ...this.val().map((i) => parseInt(i)),
                    ...(options.excluded ? options.excluded() : [])
                ]
            };
        },
    };
    if (!!options.result_converter) {
        Object.assign(params, {
            processResults: function (data) {
                return {results: data.results.map(options.result_converter)};
            }
        });
    }
    return {ajax: params};
}
