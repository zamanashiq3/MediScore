#!/bin/bash
clean=FALSE

echo
echo "CASE 1: VALIDATING SCORING OF TARGET REGIONS"
echo

python2 MaskScorer.py -t manipulation --refDir ../../data/test_suite/maskScorerTests -r reference/manipulation/NC2017-manipulation-ref.csv -x indexes/NC2017-manipulation-index.csv -s ../../data/test_suite/maskScorerTests/B_NC2017_Manipulation_ImgOnly_c-me2_1/B_NC2017_Manipulation_ImgOnly_c-me2_1.csv -oR ../../data/test_suite/maskScorerTests/target_all -html
python2 MaskScorer.py -t manipulation --refDir ../../data/test_suite/maskScorerTests -r reference/manipulation/NC2017-manipulation-ref.csv -x indexes/NC2017-manipulation-index.csv -s ../../data/test_suite/maskScorerTests/B_NC2017_Manipulation_ImgOnly_c-me2_1/B_NC2017_Manipulation_ImgOnly_c-me2_1.csv -oR ../../data/test_suite/maskScorerTests/target_clone -html -tmt 'clone'
python2 MaskScorer.py -t manipulation --refDir ../../data/test_suite/maskScorerTests -r reference/manipulation/NC2017-manipulation-ref.csv -x indexes/NC2017-manipulation-index.csv -s ../../data/test_suite/maskScorerTests/B_NC2017_Manipulation_ImgOnly_c-me2_1/B_NC2017_Manipulation_ImgOnly_c-me2_1.csv -oR ../../data/test_suite/maskScorerTests/target_add -html -tmt 'add'
python2 MaskScorer.py -t manipulation --refDir ../../data/test_suite/maskScorerTests -r reference/manipulation/NC2017-manipulation-ref.csv -x indexes/NC2017-manipulation-index.csv -s ../../data/test_suite/maskScorerTests/B_NC2017_Manipulation_ImgOnly_c-me2_1/B_NC2017_Manipulation_ImgOnly_c-me2_1.csv -oR ../../data/test_suite/maskScorerTests/target_removal -html -tmt 'removal' #not present in the picture, not present in the journal
python2 MaskScorer.py -t manipulation --refDir ../../data/test_suite/maskScorerTests -r reference/manipulation/NC2017-manipulation-ref.csv -x indexes/NC2017-manipulation-index.csv -s ../../data/test_suite/maskScorerTests/B_NC2017_Manipulation_ImgOnly_c-me2_1/B_NC2017_Manipulation_ImgOnly_c-me2_1.csv -oR ../../data/test_suite/maskScorerTests/target_clone_add -html -tmt 'clone,add'
python2 MaskScorer.py -t manipulation --refDir ../../data/test_suite/maskScorerTests -r reference/manipulation/NC2017-manipulation-ref.csv -x indexes/NC2017-manipulation-index.csv -s ../../data/test_suite/maskScorerTests/B_NC2017_Manipulation_ImgOnly_c-me2_1/B_NC2017_Manipulation_ImgOnly_c-me2_1.csv -oR ../../data/test_suite/maskScorerTests/target_heal -html -tmt 'heal' #not present in the picture,but present in the journal
python2 MaskScorer.py -t manipulation --refDir ../../data/test_suite/maskScorerTests -r reference/manipulation/NC2017-manipulation-ref.csv -x indexes/NC2017-manipulation-index.csv -s ../../data/test_suite/maskScorerTests/B_NC2017_Manipulation_ImgOnly_c-me2_1/B_NC2017_Manipulation_ImgOnly_c-me2_1.csv -oR ../../data/test_suite/maskScorerTests/target_remove -html -tmt 'remove'

diff ../../data/test_suite/maskScorerTests/target_all/B_NC2017_Manipulation_ImgOnly_c-me2_1-mask_score.csv ../../data/test_suite/maskScorerTests/ref_maskreport_all.csv > comp_maskreport_all.txt
diff ../../data/test_suite/maskScorerTests/target_all/B_NC2017_Manipulation_ImgOnly_c-me2_1-mask_scores_perimage.csv ../../data/test_suite/maskScorerTests/ref_maskreport_all-perimage.csv > comp_maskreport_all-perimage.txt
diff ../../data/test_suite/maskScorerTests/target_all/B_NC2017_Manipulation_ImgOnly_c-me2_1-journalResults.csv ../../data/test_suite/maskScorerTests/ref_maskreport_all-journalResults.csv > comp_maskreport_all-journalResults.txt

diff ../../data/test_suite/maskScorerTests/target_clone/B_NC2017_Manipulation_ImgOnly_c-me2_1-mask_score.csv ../../data/test_suite/maskScorerTests/ref_maskreport_clone.csv > comp_maskreport_clone.txt
diff ../../data/test_suite/maskScorerTests/target_clone/B_NC2017_Manipulation_ImgOnly_c-me2_1-mask_scores_perimage.csv ../../data/test_suite/maskScorerTests/ref_maskreport_clone-perimage.csv > comp_maskreport_clone-perimage.txt
diff ../../data/test_suite/maskScorerTests/target_clone/B_NC2017_Manipulation_ImgOnly_c-me2_1-journalResults.csv ../../data/test_suite/maskScorerTests/ref_maskreport_clone-journalResults.csv > comp_maskreport_clone-journalResults.txt

diff ../../data/test_suite/maskScorerTests/target_add/B_NC2017_Manipulation_ImgOnly_c-me2_1-mask_score.csv ../../data/test_suite/maskScorerTests/ref_maskreport_add.csv > comp_maskreport_add.txt
diff ../../data/test_suite/maskScorerTests/target_add/B_NC2017_Manipulation_ImgOnly_c-me2_1-mask_scores_perimage.csv ../../data/test_suite/maskScorerTests/ref_maskreport_add-perimage.csv > comp_maskreport_add-perimage.txt
diff ../../data/test_suite/maskScorerTests/target_add/B_NC2017_Manipulation_ImgOnly_c-me2_1-journalResults.csv ../../data/test_suite/maskScorerTests/ref_maskreport_add-journalResults.csv > comp_maskreport_add-journalResults.txt

#there should be no files in the removal folder

diff ../../data/test_suite/maskScorerTests/target_clone_add/B_NC2017_Manipulation_ImgOnly_c-me2_1-mask_score.csv ../../data/test_suite/maskScorerTests/ref_maskreport_clone_add.csv > comp_maskreport_clone_add.txt
diff ../../data/test_suite/maskScorerTests/target_clone_add/B_NC2017_Manipulation_ImgOnly_c-me2_1-mask_scores_perimage.csv ../../data/test_suite/maskScorerTests/ref_maskreport_clone_add-perimage.csv > comp_maskreport_clone_add-perimage.txt
diff ../../data/test_suite/maskScorerTests/target_clone_add/B_NC2017_Manipulation_ImgOnly_c-me2_1-journalResults.csv ../../data/test_suite/maskScorerTests/ref_maskreport_clone_add-journalResults.csv > comp_maskreport_clone_add-journalResults.txt

#heal should only have journalResults to validate that nothing was scored
diff ../../data/test_suite/maskScorerTests/target_heal/B_NC2017_Manipulation_ImgOnly_c-me2_1-journalResults.csv ../../data/test_suite/maskScorerTests/ref_maskreport_heal-journalResults.csv > comp_maskreport_heal-journalResults.txt

diff ../../data/test_suite/maskScorerTests/target_remove/B_NC2017_Manipulation_ImgOnly_c-me2_1-mask_score.csv ../../data/test_suite/maskScorerTests/ref_maskreport_remove.csv > comp_maskreport_remove.txt
diff ../../data/test_suite/maskScorerTests/target_remove/B_NC2017_Manipulation_ImgOnly_c-me2_1-mask_scores_perimage.csv ../../data/test_suite/maskScorerTests/ref_maskreport_remove-perimage.csv > comp_maskreport_remove-perimage.txt
diff ../../data/test_suite/maskScorerTests/target_remove/B_NC2017_Manipulation_ImgOnly_c-me2_1-journalResults.csv ../../data/test_suite/maskScorerTests/ref_maskreport_remove-journalResults.csv > comp_maskreport_remove-journalResults.txt

#flags
flag_all=1
flag_allpi=1
flag_alljr=1
flag_clone=1
flag_clonepi=1
flag_clonejr=1
flag_add=1
flag_addpi=1
flag_addjr=1
flag_clone_add=1
flag_clone_addpi=1
flag_clone_addjr=1
flag_healjr=1
flag_remove=1
flag_removepi=1
flag_removejr=1

#filters to evaluate
filter_all="cat comp_maskreport_all.txt | grep -v -CVS"
filter_allpi="cat comp_maskreport_all-perimage.txt | grep -v -CVS"
filter_alljr="cat comp_maskreport_all-journalResults.txt | grep -v -CVS"
filter_clone="cat comp_maskreport_clone.txt | grep -v -CVS"
filter_clonepi="cat comp_maskreport_clone-perimage.txt | grep -v -CVS"
filter_clonejr="cat comp_maskreport_clone-journalResults.txt | grep -v -CVS"
filter_add="cat comp_maskreport_add.txt | grep -v -CVS"
filter_addpi="cat comp_maskreport_add-perimage.txt | grep -v -CVS"
filter_addjr="cat comp_maskreport_add-journalResults.txt | grep -v -CVS"
filter_clone_add="cat comp_maskreport_clone_add.txt | grep -v -CVS"
filter_clone_addpi="cat comp_maskreport_clone_add-perimage.txt | grep -v -CVS"
filter_clone_addjr="cat comp_maskreport_clone_add-journalResults.txt | grep -v -CVS"
filter_healjr="cat comp_maskreport_heal-journalResults.txt | grep -v -CVS"
filter_remove="cat comp_maskreport_remove.txt | grep -v -CVS"
filter_removepi="cat comp_maskreport_remove-perimage.txt | grep -v -CVS"
filter_removejr="cat comp_maskreport_remove-journalResults.txt | grep -v -CVS"

if ([ -f comp_maskreport_removal.txt -o -f comp_maskreport_removal-perimage.txt -o -f comp_maskreport_removal-journalResults.txt \
 -o -f comp_maskreport_heal.txt -o -f comp_maskreport_heal-perimage.txt \
]); then
  echo
  echo "    !!!!! MASK SCORER TEST FAILED AT CASE 1 !!!!!    "
  echo "     EXTRA FILES PRESENT     "
  echo
  exit
fi
 
if ([ ! -f comp_maskreport_all.txt -o ! -f comp_maskreport_all-perimage.txt -o ! -f comp_maskreport_all-journalResults.txt \
 -o ! -f comp_maskreport_clone.txt -o ! -f comp_maskreport_clone-perimage.txt -o ! -f comp_maskreport_clone-journalResults.txt \
 -o ! -f comp_maskreport_add.txt -o ! -f comp_maskreport_add-perimage.txt -o ! -f comp_maskreport_add-journalResults.txt \
 -o ! -f comp_maskreport_clone_add.txt -o ! -f comp_maskreport_clone_add-perimage.txt -o ! -f comp_maskreport_clone_add-journalResults.txt \
 -o ! -f comp_maskreport_remove.txt -o ! -f comp_maskreport_remove-perimage.txt -o ! -f comp_maskreport_remove-journalResults.txt \
 -o ! -f comp_maskreport_heal-journalResults.txt \
]); then
  echo
  echo "    !!!!! MASK SCORER TEST FAILED AT CASE 1 !!!!!    "
  echo "     MISSING FILES ABSENT     "
  echo
  exit
fi

#TODO: update the testing script accordingly with CASE 1 and CASE 2

if test "`eval $filter_all`" = "" ; then
  flag_all=0
	if [ $clean = "TRUE" ] ; then
		rm ../../data/test_suite/maskScorerTests/maniptest/B_NC2017_Manipulation_ImgOnly_c-me2_1-mask_score.csv
	fi
	rm comp_maskreport_manip.txt
else
	echo comp_maskreport_manip.txt
	cat comp_maskreport_manip.txt
fi

if test "`eval $filter_allpi`" = "" ; then
  flag_allpi=0
	if [ $clean = "TRUE" ] ; then
		rm ../../data/test_suite/maskScorerTests/maniptest/B_NC2017_Manipulation_ImgOnly_c-me2_1-mask_scores_perimage.csv
	fi
	rm comp_maskreport_manip-perimage.txt
else
	echo comp_maskreport_manip-perimage.txt
	cat comp_maskreport_manip-perimage.txt
fi

if test "`eval $filter_alljr`" = "" ; then
  flag_alljr=0
	if [ $clean = "TRUE" ] ; then
		rm ../../data/test_suite/maskScorerTests/maniptest/B_NC2017_Manipulation_ImgOnly_c-me2_1-journalResults.csv
	fi
	rm comp_maskreport_manip-journalResults.txt
else
	echo comp_maskreport_manip-journalResults.txt
	cat comp_maskreport_manip-journalResults.txt
fi

if ([ $flag_all == 0 -a $flag_allpi == 0 -a $flag_alljr == 0 ]); then
  echo
  echo "CASE 1 SUCCESSFULLY PASSED"
  echo
	if [ $clean = "TRUE" ] ; then
		rm -rf ../../data/test_suite/maskScorerTests/splicetest
		rm -rf ../../data/test_suite/maskScorerTests/maniptest
	fi
else
  echo
  echo "    !!!!! MASK SCORER TEST FAILED AT CASE 1 !!!!!    "
  echo
  exit
fi

