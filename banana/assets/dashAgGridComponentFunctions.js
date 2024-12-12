var dagcomponentfuncs = window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};

dagcomponentfuncs.DMC_ColorInput = function (props) {
    const { setData, data, field } = props;

    function onChangeEnd(color) {
        const updatedData = { ...data };
        updatedData[field] = color;
        setData(updatedData);
    }

    return React.createElement(
        "div",
        {
            style: {
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                height: "100%",
            },
        },
        React.createElement(
            window.dash_mantine_components.ColorInput,
            {
                value: data[field],
                onChangeEnd,
                format: 'hex',
                withPicker: false,
                style: {
                    margin: "0",
                    width: "100%",
                },
            }
        )
    );
};
