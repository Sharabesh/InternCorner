/**
 * Created by sharabra on 7/14/17.
 */
/**
 * User: andrew.alba
 * Date: 10/21/15
 * Copyright 2015 Alba Web Studio. All rights reserved.
 */
if( typeof(ALBA) === "undefined" || ALBA === null ){
	ALBA = {};
}
ALBA.ModalBuilder = function() {
	/**
	 * Builds #tmpModal disposable modal on the fly
	 * based on specific object passed
	 * @param obj
	 * @... {String} obj.modalTitle
	 * @... {Array} obj.modalContent
	 * @returns {boolean}
	 */
	function bm(obj) {
		var obj=obj || {},
			title=obj.modalTitle || '',
			content=obj.modalContent || [];
		// we need obj.modalTitle and an obj.modalContent [an array] to build this properly
		var $modal,
			$modalDialog,
			$modalContent,
			$modalHeader;
		if (!$('#tmpModal').length) { // if it isn't there, build it

			$modal=$('<div></div>').attr('id','tmpModal').addClass('modal fade');
			$modalDialog=$('<div></div>').addClass('modal-dialog modal-lg');
			$modalContent=$('<div></div>').addClass('modal-content');
			$modalHeader=$('<div></div>').addClass('modal-header').html(
				'<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>' +
				'<h4 class="modal-title">' + title + '</h4>'
			);
			$modalContent.append($modalHeader);
			for(var i=0; i<content.length; i++) {
				$modalContent.append(content[i]);
			}
			$('body').append($modal.append($modalDialog.append($modalContent)));
		}
		$('#tmpModal').modal({show:true});
		$('#tmpModal').on('hidden.bs.modal', function() {
			// destroy tmpModal
			$(this).remove();
		});
		return false;
	}

	/**
	 * Pass in form element attributes as object
	 * @param obj
	 * @... {string} obj.inputType
	 * @... {object} obj.elAttr
	 * @... {string} obj.elClass
	 * @... {string} obj.defaultValue
	 * @... {object} obj.label
	 * @... {boolean} obj.hasFeedback
	 * @... {object} obj.onEvent
	 * @... {array|object} obj.optionArgs (specific to select input type)
	 * @... {string} obj.optionDefault
	 * @... {object} obj.inputGroup
	 * @... {boolean} obj.isChecked
	 * @returns {DOM element}
	 */

	function bmFormEl(obj) {
		var obj=obj || {},
			inputType=obj.inputType || 'text',
			elAttr=obj.elAttr || {},
			elClass=obj.elClass || 'form-control',
			defaultVal=obj.defaultVal || '',
			label=obj.label || {},
			labelId=obj.label.id || '',
			labelClass=obj.label.class || 'control-label',
			labelHtml=obj.label.html || '',
			hasFeedback=obj.hasFeedback || false,
			onEvent=obj.onEvent || {},
			optionArgs=obj.optionArgs || [],
			optionDefault=obj.optionDefault || '',
			inputGroup=obj.inputGroup || {},
			isChecked=obj.isChecked || false,
			formGroupHide=obj.hideFormGroup || false,
			$formGroup=$('<div></div>'),
			$label=$('<label></label>'),
			$inputGroup,
			$formControl;
		if (inputType !== 'checkbox' && inputType !== 'radio' && inputType !== 'hidden') {
			$formGroup.addClass('form-group');
		}
		else {
			if (inputType !== 'hidden') {
				$formGroup.addClass(inputType);
			}
		}
		if (formGroupHide) {
			$formGroup.addClass('hide');
		}
		if (hasFeedback) {
			$formGroup.addClass('has-feedback');
		}

		if (inputType == 'textarea') {
			elAttr.rows=6;
			$formControl=$('<textarea></textarea>').attr(elAttr);
		}
		else if (inputType == 'select') {
			$formControl=$('<select></select>').attr(elAttr);
			if (Object.prototype.toString.call(optionArgs) === '[object Array]' && optionArgs.length > 0) {
				for (var i=0; i < optionArgs.length; i++) {
					$formControl.append('<option>' + optionArgs[i] + '</option>');
				}
			}
			if (Object.prototype.toString.call(optionArgs) === '[object Object]' && !$.isEmptyObject(optionArgs)) {
				for (var opt in optionArgs) {
					if (optionArgs.hasOwnProperty(opt)) {
						$formControl.append('<option value="' + opt + '">' + optionArgs[opt] + '</option>');
					}
				}
			}
			if (optionDefault !== '') {
				$formControl.val(optionDefault);
			}
		}
		else {
			elAttr.type=inputType;
			$formControl=$('<input/>').attr(elAttr);
		}
		if ((inputType === 'checkbox' || inputType === 'radio') && isChecked) {
			$formControl.prop('checked','checked');
		}
		if (elClass !== '') {
			$formControl.addClass(elClass);
		}
		if (defaultVal !== '') {
			$formControl.val(defaultVal);
		}
		if (!$.isEmptyObject(onEvent)) {
			$formControl.on(onEvent.events, onEvent.eventhandler);
		}
		if (!$.isEmptyObject(label)) {
			$label.attr({for:labelId}).html(labelHtml);
			if (inputType !== 'checkbox' && inputType !== 'radio' && inputType !== 'hidden') {
				$label.addClass(labelClass);
			}
		}
		if (!$.isEmptyObject(inputGroup)) {
			$inputGroup=$('<div></div>').addClass('input-group');
			if (typeof inputGroup.prepend !== 'undefined') {
				$inputGroup.append($('<div></div>').addClass('input-group-addon').html(inputGroup.prepend));
			}
			$inputGroup.append($formControl);
			if (typeof inputGroup.append !== 'undefined') {
				$inputGroup.append($('<div></div>').addClass('input-group-addon').html(inputGroup.append));
			}
		}
		else {
			$inputGroup=$formControl;
		}
		if (inputType !== 'checkbox' && inputType !== 'radio') {
			if (inputType !== 'hidden') {
				return $formGroup.append($label).append($inputGroup);
			}
			else {
				return $formGroup.append($inputGroup);
			}
		}
		else {
			return $formGroup.append($label.prepend($inputGroup));
		}
	}

	return {
		buildModal: function(obj) {
			bm(obj);
		},
		buildModalFormElements: function(obj) {
			return bmFormEl(obj);
		}
	};
}();